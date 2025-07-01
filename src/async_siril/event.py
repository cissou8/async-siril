import asyncio
import structlog.stdlib
import typing as t
import os
import re

logger = structlog.stdlib.get_logger()

# Custom pipes for Siril CLI communications
custom_read_pipe_name = "/tmp/async_siril_command.out"
custom_write_pipe_name = "/tmp/async_siril_command.in"


class SirilEvent:
    LOG = "log"
    PROGRESS = "progress"
    STATUS = "status"

    def __init__(self, raw_string: str):
        self.status = None
        self.message = None
        self.progress = 0
        self._raw_string = raw_string

        if raw_string.startswith("status:"):
            self.value = SirilEvent.STATUS
            self._parse_status_output()
        elif raw_string.startswith("progress:"):
            self.value = SirilEvent.PROGRESS
            self._parse_progress_output()
        elif raw_string.startswith("log:"):
            self.value = SirilEvent.LOG
            self._parse_log_output()
        elif raw_string == "ready":
            self.value = SirilEvent.STATUS
            self._parse_ready_output()
        else:
            self.value = SirilEvent.LOG
            self.message = raw_string

    def __str__(self):
        return self._raw_string

    def _parse_status_output(self):
        matches = re.search(r"status\:\s(\S*)\s(.*)", self._raw_string)
        self.status = matches.group(1)
        self.message = matches.group(2)

    def _parse_log_output(self):
        matches = re.search(r"log\:\s(.*)", self._raw_string)
        self.message = matches.group(1)

    def _parse_progress_output(self):
        matches = re.search(r"progress\:\s(\d*)", self._raw_string)
        self.progress = int(matches.group(1))

    def _parse_ready_output(self):
        self.status = self._raw_string

    @property
    def completed(self) -> bool:
        return self.status == "success" or self.status == "error" or self.status == "exit"

    @property
    def errored(self) -> bool:
        return self.status == "error"

    @property
    def siril_ready(self) -> bool:
        return self.status == "ready"


class AsyncSirilEventConsumer:
    def __init__(self):
        loop = asyncio.get_event_loop()
        self.queue = asyncio.Queue()
        self.fifo_path = custom_read_pipe_name
        self.fifo_closed = loop.create_future()
        self.siril_ready = loop.create_future()
        self._running = False

        # clean up from last run
        self._safe_remove_fifo()

    def start(self) -> asyncio.Task:
        """Return a task that runs the consumer loop in the background."""
        self._running = True
        self._task = asyncio.create_task(self._run(), name=type(self).__name__)
        return self._task

    def stop(self):
        if self._running:
            logger.info("Stopping consumer fifo pipe")
            self._running = False
        
        if self._task:
            self._task.cancel()

        self._safe_remove_fifo()

    async def _run(self):
        """Main consumer loop that waits for writers and reads FIFO."""
        if not os.path.exists(self.fifo_path):
            os.mkfifo(self.fifo_path)

        while self._running:
            try:
                with open(self.fifo_path, "r") as fifo:
                    logger.info("Consumer fifo pipe opened")

                    async for event in self._aiter_events(fifo):
                        if event.siril_ready:
                            logger.info("Consumer received ready event")
                            self.siril_ready.set_result(None)
                        else:
                            self.queue.put_nowait(event)
                    
                    logger.info("EOF from the consumer")
            except Exception as e:
                logger.info(f"Error in consumer task: {e}")
                await asyncio.sleep(1)

    async def _aiter_events(self, file_obj) -> t.AsyncGenerator[SirilEvent, None]:
        """Asynchronously yield events from a blocking file object."""
        loop = asyncio.get_event_loop()
        while self._running:
            line = await loop.run_in_executor(None, file_obj.readline)
            if line == "":
                logger.info("Consumer fifo pipe closed")
                self.fifo_closed.set_result(None)
                break
            yield SirilEvent(line.rstrip())
    
    def _safe_remove_fifo(self):
        try:
            if os.path.exists(self.fifo_path):
                os.remove(self.fifo_path)
        except OSError as e:
            logger.error("Failed to remove Consumer FIFO: %s" % e)


class AsyncSirilCommandProducer:
    def __init__(self):
        self._loop = asyncio.get_event_loop()
        self._queue = asyncio.Queue()
        self._writer = None
        self._task = None
        self._running = False
        self.fifo_path = custom_write_pipe_name
        self.fifo_closed = self._loop.create_future()

        # clean up from last run
        self._safe_remove_fifo()

    def start(self) -> asyncio.Task:
        """Starts the background writer task."""
        self._running = True
        self._task = asyncio.create_task(self._run(), name=type(self).__name__)
        return self._task

    def stop(self):
        """Gracefully stop the background writer."""
        if self._running:
            logger.info("Stopping producer fifo pipe")
            self._running = False
            self.fifo_closed.set_result(None)

        if self._task:
            self._task.cancel()

        self._safe_remove_fifo()

    async def send(self, command: str):
        """Send a message to be written to the FIFO."""
        await self._queue.put(command)

    async def _run(self):
        """Main producer loop that waits for messages and writes them to the FIFO."""
        if not os.path.exists(self.fifo_path):
            os.mkfifo(self.fifo_path)
        
        try:
            # Block until a reader opens the FIFO
            self._writer = await self._loop.run_in_executor(None, lambda: open(self.fifo_path, "w"))

            while self._running:
                try:
                    message = await self._queue.get()
                    await self._loop.run_in_executor(None, self._write_line, message)
                except asyncio.CancelledError:
                    break
        finally:
            if self._writer:
                self._writer.close()

        logger.info("The producer was nicely stopped.")

    def _write_line(self, message: str):
        self._writer.write(message + "\n")
        self._writer.flush()
    
    def _safe_remove_fifo(self):
        try:
            if os.path.exists(self.fifo_path):
                os.remove(self.fifo_path)
        except OSError as e:
            logger.error("Failed to remove Producer FIFO: %s" % e)
