import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

from async_siril.event import AsyncSirilEventConsumer, AsyncSirilCommandProducer, SirilEvent, PipeMode


class TestAsyncSirilEventConsumer:
    @pytest.fixture
    def consumer(self):
        with patch("async_siril.event.PipeClient") as mock_pipe_client:
            mock_instance = Mock()
            mock_instance.path = "/tmp/test_pipe"
            mock_instance.connect = AsyncMock()
            mock_instance.read_line = AsyncMock()
            mock_instance.close = Mock()
            mock_pipe_client.return_value = mock_instance
            return AsyncSirilEventConsumer()

    def test_consumer_initialization(self, consumer):
        assert consumer._running is False
        assert isinstance(consumer.queue, asyncio.Queue)
        assert consumer.fifo_closed is not None
        assert consumer.siril_ready is not None
        assert consumer._pipe is not None

    def test_consumer_pipe_path_property(self, consumer):
        consumer._pipe.path = "/test/path"
        assert consumer.pipe_path == "/test/path"

    def test_consumer_start(self, consumer):
        with patch("asyncio.create_task") as mock_create_task:
            mock_task = Mock()
            mock_create_task.return_value = mock_task

            # Patch the _run method to avoid creating an actual coroutine
            with patch.object(consumer, "_run") as mock_run:
                mock_run.return_value = Mock()  # Return a non-coroutine
                result = consumer.start()

                assert consumer._running is True
                assert consumer._task == mock_task
                assert result == mock_task
                mock_create_task.assert_called_once()

    def test_consumer_stop_when_running(self, consumer):
        consumer._running = True
        consumer._task = Mock()
        consumer._pipe = Mock()

        consumer.stop()

        assert consumer._running is False
        consumer._task.cancel.assert_called_once()
        consumer._pipe.close.assert_called_once()

    def test_consumer_stop_when_not_running(self, consumer):
        consumer._running = False
        consumer._task = Mock()
        consumer._pipe = Mock()

        consumer.stop()

        consumer._task.cancel.assert_called_once()
        consumer._pipe.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_consumer_run_not_running(self, consumer):
        consumer._running = False

        await consumer._run()

        # Should return early without doing anything
        consumer._pipe.connect.assert_not_called()

    @pytest.mark.asyncio
    async def test_consumer_run_successful(self, consumer):
        consumer._running = True
        consumer._pipe.connect = AsyncMock()

        # Mock the async iterator properly
        mock_events = [SirilEvent("ready"), SirilEvent("log: test message"), SirilEvent("status: success completed")]

        async def mock_aiter_events():
            for event in mock_events:
                yield event

        with patch.object(consumer, "_aiter_events", return_value=mock_aiter_events()):
            await consumer._run()

            consumer._pipe.connect.assert_called_once()
            assert consumer.siril_ready.done()

    @pytest.mark.asyncio
    async def test_consumer_run_with_exception(self, consumer):
        consumer._running = True
        consumer._pipe.connect = AsyncMock(side_effect=Exception("Connection failed"))

        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            await consumer._run()

            mock_sleep.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_consumer_aiter_events(self, consumer):
        consumer._running = True
        consumer._pipe.read_line = AsyncMock(
            side_effect=[
                "log: test message",
                "status: success",
                "",  # EOF
            ]
        )

        events = []
        async for event in consumer._aiter_events():
            events.append(event)

        assert len(events) == 2
        assert events[0]._raw_string == "log: test message"
        assert events[1]._raw_string == "status: success"
        assert consumer.fifo_closed.done()

    @pytest.mark.asyncio
    async def test_consumer_aiter_events_not_running(self, consumer):
        consumer._running = False

        events = []
        async for event in consumer._aiter_events():
            events.append(event)

        assert len(events) == 0

    @pytest.mark.asyncio
    async def test_consumer_ready_event_handling(self, consumer):
        consumer._running = True
        consumer._pipe.connect = AsyncMock()

        ready_event = SirilEvent("ready")
        log_event = SirilEvent("log: test")

        async def mock_aiter_events():
            yield ready_event
            yield log_event

        with patch.object(consumer, "_aiter_events", return_value=mock_aiter_events()):
            await consumer._run()

            # Ready event should set the future, not go to queue
            assert consumer.siril_ready.done()
            # Log event should go to queue
            assert consumer.queue.qsize() == 1
            queued_event = consumer.queue.get_nowait()
            assert queued_event._raw_string == "log: test"


class TestAsyncSirilCommandProducer:
    @pytest.fixture
    def producer(self):
        with patch("async_siril.event.PipeClient") as mock_pipe_client:
            mock_instance = Mock()
            mock_instance.path = "/tmp/test_pipe"
            mock_instance.connect = AsyncMock()
            mock_instance.write_line = AsyncMock()
            mock_instance.close = Mock()
            mock_pipe_client.return_value = mock_instance
            return AsyncSirilCommandProducer()

    def test_producer_initialization(self, producer):
        assert producer._running is False
        assert isinstance(producer._queue, asyncio.Queue)
        assert producer.fifo_closed is not None
        assert producer._task is None
        assert producer._pipe is not None

    def test_producer_pipe_path_property(self, producer):
        producer._pipe.path = "/test/path"
        assert producer.pipe_path == "/test/path"

    def test_producer_start(self, producer):
        with patch("asyncio.create_task") as mock_create_task:
            mock_task = Mock()
            mock_create_task.return_value = mock_task

            # Patch the _run method to avoid creating an actual coroutine
            with patch.object(producer, "_run") as mock_run:
                mock_run.return_value = Mock()  # Return a non-coroutine
                result = producer.start()

                assert producer._running is True
                assert producer._task == mock_task
                assert result == mock_task
                mock_create_task.assert_called_once()

    def test_producer_stop_when_running(self, producer):
        producer._running = True
        producer._task = Mock()
        producer._pipe = Mock()

        producer.stop()

        assert producer._running is False
        assert producer.fifo_closed.done()
        producer._task.cancel.assert_called_once()
        producer._pipe.close.assert_called_once()

    def test_producer_stop_when_not_running(self, producer):
        producer._running = False
        producer._task = Mock()
        producer._pipe = Mock()

        producer.stop()

        producer._task.cancel.assert_called_once()
        producer._pipe.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_producer_send(self, producer):
        command = "test command"

        await producer.send(command)

        # Command should be in the queue
        queued_command = await producer._queue.get()
        assert queued_command == command

    @pytest.mark.asyncio
    async def test_producer_run_not_running(self, producer):
        producer._running = False

        await producer._run()

        # Should return early without doing anything
        producer._pipe.connect.assert_not_called()

    @pytest.mark.asyncio
    async def test_producer_run_successful(self, producer):
        producer._running = True
        producer._pipe.connect = AsyncMock()
        producer._pipe.write_line = AsyncMock()
        producer._pipe.close = Mock()

        # Mock the queue to return one command then stop
        call_count = {"value": 0}

        async def mock_get():
            call_count["value"] += 1
            if call_count["value"] == 1:
                return "test command"
            else:
                producer._running = False
                raise asyncio.CancelledError()

        with patch.object(producer._queue, "get", side_effect=mock_get):
            try:
                await producer._run()
            except asyncio.CancelledError:
                pass

        producer._pipe.connect.assert_called_once()
        producer._pipe.write_line.assert_called_with("test command")
        producer._pipe.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_producer_run_with_cancelled_error(self, producer):
        producer._running = True
        producer._pipe.connect = AsyncMock()
        producer._pipe.close = Mock()

        # Mock queue.get to raise CancelledError
        with patch.object(producer._queue, "get", side_effect=asyncio.CancelledError):
            await producer._run()

        producer._pipe.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_producer_multiple_commands(self, producer):
        producer._running = True
        producer._pipe.connect = AsyncMock()
        producer._pipe.write_line = AsyncMock()
        producer._pipe.close = Mock()

        commands = ["command1", "command2", "command3"]
        state = {"index": 0}

        async def mock_get():
            if state["index"] < len(commands):
                cmd = commands[state["index"]]
                state["index"] += 1
                return cmd
            else:
                producer._running = False
                raise asyncio.CancelledError()

        with patch.object(producer._queue, "get", side_effect=mock_get):
            try:
                await producer._run()
            except asyncio.CancelledError:
                pass

        # Should have written all commands
        assert producer._pipe.write_line.call_count == len(commands)
        for cmd in commands:
            producer._pipe.write_line.assert_any_call(cmd)


class TestIntegrationScenarios:
    @pytest.mark.asyncio
    async def test_consumer_producer_pipe_paths_different(self):
        with patch("async_siril.event.PipeClient") as mock_pipe_client:
            # Mock different paths for read and write pipes
            def side_effect(mode, **_kwargs):
                mock_instance = Mock()
                if mode == PipeMode.READ:
                    mock_instance.path = "/tmp/siril_command.out"
                else:
                    mock_instance.path = "/tmp/siril_command.in"
                return mock_instance

            mock_pipe_client.side_effect = side_effect

            consumer = AsyncSirilEventConsumer()
            producer = AsyncSirilCommandProducer()

            assert consumer.pipe_path != producer.pipe_path
            assert consumer.pipe_path == "/tmp/siril_command.out"
            assert producer.pipe_path == "/tmp/siril_command.in"

    @pytest.mark.asyncio
    async def test_consumer_producer_lifecycle(self):
        with patch("async_siril.event.PipeClient"):
            consumer = AsyncSirilEventConsumer()
            producer = AsyncSirilCommandProducer()

            # Patch _run methods to avoid creating actual coroutines
            with (
                patch.object(consumer, "_run") as mock_consumer_run,
                patch.object(producer, "_run") as mock_producer_run,
            ):
                mock_consumer_run.return_value = Mock()
                mock_producer_run.return_value = Mock()

                # Start both
                consumer_task = consumer.start()
                producer_task = producer.start()

                assert consumer._running is True
                assert producer._running is True
                assert consumer_task is not None
                assert producer_task is not None

                # Stop both
                consumer.stop()
                producer.stop()

                assert consumer._running is False
                assert producer._running is False

    @pytest.mark.asyncio
    async def test_event_flow_simulation(self):
        """Simulate a basic event flow between consumer and producer"""
        with patch("async_siril.event.PipeClient"):
            consumer = AsyncSirilEventConsumer()

            # Mock pipe to simulate events
            consumer._pipe.connect = AsyncMock()  # type: ignore
            consumer._pipe.read_line = AsyncMock(
                side_effect=[  # type: ignore
                    "ready",
                    "log: Starting process",
                    "progress: 50",
                    "status: success Process completed",
                    "",  # EOF
                ]
            )

            consumer._running = True
            await consumer._run()

            # Check that events were processed correctly
            assert consumer.siril_ready.done()
            assert consumer.queue.qsize() == 3  # log, progress, status events

            # Verify events in queue
            events = []
            while not consumer.queue.empty():
                events.append(consumer.queue.get_nowait())

            assert len(events) == 3
            assert events[0].value == SirilEvent.LOG
            assert events[1].value == SirilEvent.PROGRESS
            assert events[2].value == SirilEvent.STATUS

    def test_consumer_uses_read_pipe_mode(self):
        with patch("async_siril.event.PipeClient") as mock_pipe_client:
            AsyncSirilEventConsumer()

            # Verify PipeClient was called with READ mode
            mock_pipe_client.assert_called_once_with(mode=PipeMode.READ)

    def test_producer_uses_write_pipe_mode(self):
        with patch("async_siril.event.PipeClient") as mock_pipe_client:
            AsyncSirilCommandProducer()

            # Verify PipeClient was called with WRITE mode
            mock_pipe_client.assert_called_once_with(mode=PipeMode.WRITE)

    @pytest.mark.asyncio
    async def test_exception_handling_in_consumer(self):
        with patch("async_siril.event.PipeClient"):
            consumer = AsyncSirilEventConsumer()
            consumer._running = True

            # Mock connect to raise an exception
            consumer._pipe.connect = AsyncMock(side_effect=Exception("Connection failed"))  # type: ignore

            with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
                await consumer._run()

                # Should have slept after exception
                mock_sleep.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_queue_operations(self):
        """Test queue operations in both consumer and producer"""
        with patch("async_siril.event.PipeClient"):
            consumer = AsyncSirilEventConsumer()
            producer = AsyncSirilCommandProducer()

            # Test consumer queue
            test_event = SirilEvent("log: test message")
            consumer.queue.put_nowait(test_event)

            retrieved_event = consumer.queue.get_nowait()
            assert retrieved_event == test_event

            # Test producer queue
            test_command = "test command"
            await producer.send(test_command)

            retrieved_command = await producer._queue.get()
            assert retrieved_command == test_command

    def test_future_initialization(self):
        """Test that futures are properly initialized"""
        with patch("async_siril.event.PipeClient"):
            consumer = AsyncSirilEventConsumer()
            producer = AsyncSirilCommandProducer()

            # Consumer futures
            assert not consumer.fifo_closed.done()
            assert not consumer.siril_ready.done()

            # Producer futures
            assert not producer.fifo_closed.done()

    @pytest.mark.asyncio
    async def test_task_naming(self):
        """Test that tasks are created with proper names"""
        with patch("async_siril.event.PipeClient"):
            consumer = AsyncSirilEventConsumer()
            producer = AsyncSirilCommandProducer()

            with patch("asyncio.create_task") as mock_create_task:
                mock_task = Mock()
                mock_create_task.return_value = mock_task

                # Patch the _run methods to avoid creating actual coroutines
                with (
                    patch.object(consumer, "_run") as mock_consumer_run,
                    patch.object(producer, "_run") as mock_producer_run,
                ):
                    mock_consumer_run.return_value = Mock()
                    mock_producer_run.return_value = Mock()

                    consumer.start()
                    # Check that create_task was called with the right name
                    _, kwargs = mock_create_task.call_args
                    assert kwargs["name"] == "AsyncSirilEventConsumer"

                    producer.start()
                    # Check the last call
                    _, kwargs = mock_create_task.call_args
                    assert kwargs["name"] == "AsyncSirilCommandProducer"
