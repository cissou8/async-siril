import pytest
import asyncio
import subprocess
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, PropertyMock

from async_siril import SirilError, SirilCli, SirilResource
from async_siril.command import BaseCommand
from async_siril.command_types import SirilSetting


class TestSirilError:
    def test_siril_error_creation(self):
        cmd = "test_command"
        message = "Test error message"

        error = SirilError(cmd, message)

        assert error.command == cmd
        assert error.message == message
        assert str(error) == f"SirilError from command: `{cmd}` error: `{message}`"

    def test_siril_error_inheritance(self):
        error = SirilError("test", "message")

        assert isinstance(error, Exception)
        assert str(error) == "SirilError from command: `test` error: `message`"

    def test_siril_error_with_empty_strings(self):
        error = SirilError("", "")

        assert error.command == ""
        assert error.message == ""
        assert str(error) == "SirilError from command: `` error: ``"

    def test_siril_error_with_special_characters(self):
        cmd = "test_command --param='value with spaces'"
        message = "Error: file not found at /path/to/file.fits with spaces"

        error = SirilError(cmd, message)

        assert error.command == cmd
        assert error.message == message
        expected = f"SirilError from command: `{cmd}` error: `{message}`"
        assert str(error) == expected

    def test_siril_error_exception_behavior(self):
        cmd = "failing_command"
        message = "Something went wrong"

        with pytest.raises(SirilError) as exc_info:
            raise SirilError(cmd, message)

        assert exc_info.value.command == cmd
        assert exc_info.value.message == message


class TestSirilCli:
    @pytest.fixture
    def mock_subprocess_popen(self):
        with patch("subprocess.Popen") as mock_popen:
            mock_process = Mock()
            mock_process.communicate.return_value = (b"siril-cli 1.2.3\n", b"")
            mock_popen.return_value = mock_process
            yield mock_popen

    @pytest.fixture
    def mock_siril_exe_exists(self):
        with patch("os.path.exists", return_value=True):
            yield

    @pytest.fixture
    def siril_cli(self, mock_subprocess_popen, mock_siril_exe_exists):
        with patch.object(SirilCli, "_find_siril_cli", return_value="siril-cli"):
            return SirilCli()

    def test_siril_cli_initialization_default(self, mock_subprocess_popen, mock_siril_exe_exists):
        with patch.object(SirilCli, "_find_siril_cli", return_value="siril-cli"):
            cli = SirilCli()

            assert cli._siril_exe == "siril-cli"
            assert cli._cwd is None
            assert isinstance(cli._resources, SirilResource)
            assert cli._process is None
            assert cli.version == "siril-cli 1.2.3"

    def test_siril_cli_initialization_with_params(self, mock_subprocess_popen):
        custom_path = Path("/custom/path")
        custom_resources = SirilResource(cpu_limit=4, memory_limit="8192", memory_percent=0.8)  # type: ignore

        with patch.object(SirilCli, "_find_siril_cli", return_value="/usr/bin/siril-cli"):
            cli = SirilCli(siril_exe="custom-siril", directory=custom_path, resources=custom_resources)

            assert cli._siril_exe == "/usr/bin/siril-cli"
            assert cli._cwd == custom_path
            assert cli._resources == custom_resources

    def test_find_siril_cli_existing_path(self):
        with patch("os.path.exists", return_value=True):
            cli = SirilCli.__new__(SirilCli)  # Create without __init__
            result = cli._find_siril_cli("/custom/path/siril-cli")

            assert result == "/custom/path/siril-cli"

    def test_find_siril_cli_windows_paths(self):
        with patch("platform.system", return_value="Windows"), patch("os.path.exists") as mock_exists:
            # First call (custom path) returns False, second call (msys2 path) returns True
            mock_exists.side_effect = [False, True]

            cli = SirilCli.__new__(SirilCli)
            result = cli._find_siril_cli("siril-cli")

            assert result == "C:/msys64/mingw64/bin/siril-cli.exe"

    def test_find_siril_cli_darwin_paths(self):
        with patch("platform.system", return_value="Darwin"), patch("os.path.exists") as mock_exists:
            # First call (custom path) returns False, second call (app path) returns True
            mock_exists.side_effect = [False, True]

            cli = SirilCli.__new__(SirilCli)
            result = cli._find_siril_cli("siril-cli")

            assert result == "/Applications/Siril.app/Contents/MacOS/siril-cli"

    def test_find_siril_cli_linux_paths(self):
        with patch("platform.system", return_value="Linux"), patch("os.path.exists") as mock_exists:
            # First call (custom path) returns False, second call (local bin) returns True
            mock_exists.side_effect = [False, True]

            cli = SirilCli.__new__(SirilCli)
            result = cli._find_siril_cli("siril-cli")

            assert result == "/usr/local/bin/siril-cli"

    def test_find_siril_cli_not_found(self):
        with patch("platform.system", return_value="Linux"), patch("os.path.exists", return_value=False):
            cli = SirilCli.__new__(SirilCli)

            with pytest.raises(FileNotFoundError, match="Siril CLI executable not found"):
                cli._find_siril_cli("nonexistent-siril")

    @pytest.mark.asyncio
    async def test_start_process(self, siril_cli):
        mock_process = Mock()
        mock_process.stdout = AsyncMock()
        mock_process.stderr = AsyncMock()

        with (
            patch("asyncio.create_subprocess_exec", return_value=mock_process) as mock_create,
            patch.object(siril_cli._consumer, "start") as mock_consumer_start,
            patch.object(siril_cli._producer, "start") as mock_producer_start,
            patch.object(siril_cli._consumer, "siril_ready"),
            patch.object(siril_cli, "command"),
            patch.object(siril_cli, "set"),
            patch("asyncio.create_task"),
            patch.object(siril_cli, "_log_stream", new_callable=AsyncMock),
            patch.object(
                type(siril_cli._consumer), "pipe_path", new_callable=PropertyMock, return_value="/tmp/out_pipe"
            ),
            patch.object(
                type(siril_cli._producer), "pipe_path", new_callable=PropertyMock, return_value="/tmp/in_pipe"
            ),
        ):
            # Mock the ready future by making siril_ready a property that returns a completed future
            ready_future = asyncio.Future()
            ready_future.set_result(None)
            siril_cli._consumer.siril_ready = ready_future

            await siril_cli._start()

            # Verify subprocess was started with correct params
            mock_create.assert_called_once_with(
                "siril-cli",
                "--pipe",
                "--inpipe",
                "/tmp/in_pipe",
                "--outpipe",
                "/tmp/out_pipe",
                stdout=asyncio.subprocess.PIPE,  # type: ignore
                stderr=asyncio.subprocess.PIPE,  # type: ignore
            )

            mock_consumer_start.assert_called_once()
            mock_producer_start.assert_called_once()
            assert siril_cli._process == mock_process

    @pytest.mark.asyncio
    async def test_start_process_with_directory(self, mock_subprocess_popen, mock_siril_exe_exists):
        custom_dir = Path("/custom/working/dir")

        with patch.object(SirilCli, "_find_siril_cli", return_value="siril-cli"):
            cli = SirilCli(directory=custom_dir)

        mock_process = Mock()
        mock_process.stdout = AsyncMock()
        mock_process.stderr = AsyncMock()

        with (
            patch("asyncio.create_subprocess_exec", return_value=mock_process) as mock_create,
            patch.object(cli._consumer, "start"),
            patch.object(cli._producer, "start"),
            patch.object(cli._consumer, "siril_ready"),
            patch.object(cli, "command"),
            patch.object(cli, "set"),
            patch("asyncio.create_task"),
            patch.object(cli, "_log_stream", new_callable=AsyncMock),
            patch.object(type(cli._consumer), "pipe_path", new_callable=PropertyMock, return_value="/tmp/out_pipe"),
            patch.object(type(cli._producer), "pipe_path", new_callable=PropertyMock, return_value="/tmp/in_pipe"),
        ):
            # Mock the ready future by making siril_ready a property that returns a completed future
            ready_future = asyncio.Future()
            ready_future.set_result(None)
            cli._consumer.siril_ready = ready_future

            await cli._start()

            # Verify directory parameter was included
            mock_create.assert_called_once_with(
                "siril-cli",
                "-d",
                str(custom_dir),
                "--pipe",
                "--inpipe",
                "/tmp/in_pipe",
                "--outpipe",
                "/tmp/out_pipe",
                stdout=asyncio.subprocess.PIPE,  # type: ignore
                stderr=asyncio.subprocess.PIPE,  # type: ignore
            )

    @pytest.mark.asyncio
    async def test_stop_process(self, siril_cli):
        # Setup mock process and tasks
        mock_process = Mock()
        mock_task1 = AsyncMock()
        mock_task2 = AsyncMock()

        siril_cli._process = mock_process
        siril_cli._log_tasks = [mock_task1, mock_task2]

        with (
            patch.object(siril_cli._consumer, "stop") as mock_consumer_stop,
            patch.object(siril_cli._producer, "stop") as mock_producer_stop,
            patch("asyncio.gather", return_value=None) as mock_gather,
        ):
            await siril_cli._stop()

            mock_consumer_stop.assert_called_once()
            mock_producer_stop.assert_called_once()
            mock_process.kill.assert_called_once()
            mock_gather.assert_called_once_with(mock_task1, mock_task2, return_exceptions=True)

    @pytest.mark.asyncio
    async def test_stop_process_with_exception(self, siril_cli):
        siril_cli._process = Mock()
        siril_cli._log_tasks = []

        with (
            patch.object(siril_cli._consumer, "stop", side_effect=Exception("Stop error")),
            patch.object(siril_cli._producer, "stop"),
            patch("asyncio.gather"),
        ):
            # Should not raise exception
            await siril_cli._stop()

    @pytest.mark.asyncio
    async def test_log_stream(self, siril_cli):
        mock_stream = AsyncMock()
        mock_stream.readline.side_effect = [
            b"Line 1\n",
            b"Line 2\n",
            b"",  # EOF
        ]

        # Patch the module-level logger instead of the factory
        with patch("async_siril.siril.logger") as mock_logger:
            await siril_cli._log_stream(mock_stream, "test_stream")

            assert mock_stream.readline.call_count == 3
            assert mock_logger.info.call_count == 2

    @pytest.mark.asyncio
    async def test_command_with_string(self, siril_cli):
        with patch.object(siril_cli, "_run_command") as mock_run:
            await siril_cli.command("test_command")

            mock_run.assert_called_once_with("test_command")

    @pytest.mark.asyncio
    async def test_command_with_base_command(self, siril_cli):
        mock_cmd = Mock(spec=BaseCommand)
        mock_cmd.__str__ = Mock(return_value="base_command_str")  # type: ignore

        with patch.object(siril_cli, "_run_command") as mock_run:
            await siril_cli.command(mock_cmd)

            mock_run.assert_called_once_with("base_command_str")

    @pytest.mark.asyncio
    async def test_command_with_list_of_strings(self, siril_cli):
        commands = ["cmd1", "cmd2", "cmd3"]

        with patch.object(siril_cli, "_run_command") as mock_run:
            await siril_cli.command(commands)

            assert mock_run.call_count == 3
            mock_run.assert_any_call("cmd1")
            mock_run.assert_any_call("cmd2")
            mock_run.assert_any_call("cmd3")

    @pytest.mark.asyncio
    async def test_command_with_list_of_base_commands(self, siril_cli):
        mock_cmds = []
        for i in range(3):
            mock_cmd = Mock(spec=BaseCommand)
            mock_cmd.__str__ = Mock(return_value=f"cmd{i}")  # type: ignore
            mock_cmds.append(mock_cmd)

        with patch.object(siril_cli, "_run_command") as mock_run:
            await siril_cli.command(mock_cmds)

            assert mock_run.call_count == 3
            mock_run.assert_any_call("cmd0")
            mock_run.assert_any_call("cmd1")
            mock_run.assert_any_call("cmd2")

    @pytest.mark.asyncio
    async def test_failable_command_success(self, siril_cli):
        with patch.object(siril_cli, "command") as mock_command:
            result = await siril_cli.failable_command("success_command")

            assert result is True
            mock_command.assert_called_once_with("success_command")

    @pytest.mark.asyncio
    async def test_failable_command_failure(self, siril_cli):
        error = SirilError("fail_command", "Test error")

        with patch.object(siril_cli, "command", side_effect=error):
            result = await siril_cli.failable_command("fail_command")

            assert result is False

    @pytest.mark.asyncio
    async def test_run_command_exit(self, siril_cli):
        with patch.object(siril_cli, "stop") as mock_stop:
            await siril_cli._run_command("exit")

            mock_stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_command_success(self, siril_cli):
        # Mock successful completion event
        success_event = Mock()
        success_event.errored = False
        success_event.completed = True
        success_event.siril_ready = False

        # Mock the queue with proper sync/async methods
        mock_queue = Mock()
        mock_queue.get = AsyncMock(return_value=success_event)
        mock_queue.task_done = Mock()  # Sync method
        siril_cli._consumer.queue = mock_queue
        siril_cli._producer.send = AsyncMock()

        await siril_cli._run_command("test_command")

        siril_cli._producer.send.assert_called_once_with("test_command")
        siril_cli._consumer.queue.task_done.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_command_error(self, siril_cli):
        # Mock error event
        error_event = Mock()
        error_event.errored = True
        error_event.completed = False
        error_event.siril_ready = False
        error_event.message = "Command failed"

        # Mock the queue with proper sync/async methods
        mock_queue = Mock()
        mock_queue.get = AsyncMock(return_value=error_event)
        mock_queue.task_done = Mock()  # Sync method
        siril_cli._consumer.queue = mock_queue
        siril_cli._producer.send = AsyncMock()

        with pytest.raises(SirilError) as exc_info:
            await siril_cli._run_command("failing_command")

        assert exc_info.value.command == "failing_command"  # type: ignore
        assert exc_info.value.message == "Command failed"  # type: ignore

    @pytest.mark.asyncio
    async def test_run_command_ready(self, siril_cli):
        # Mock ready event
        ready_event = Mock()
        ready_event.errored = False
        ready_event.completed = False
        ready_event.siril_ready = True

        # Mock the queue with proper sync/async methods
        mock_queue = Mock()
        mock_queue.get = AsyncMock(return_value=ready_event)
        mock_queue.task_done = Mock()  # Sync method
        siril_cli._consumer.queue = mock_queue
        siril_cli._producer.send = AsyncMock()

        await siril_cli._run_command("ready_command")

        siril_cli._producer.send.assert_called_once_with("ready_command")
        siril_cli._consumer.queue.task_done.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_command(self, siril_cli):
        with patch.object(siril_cli, "command") as mock_command:
            await siril_cli.set(SirilSetting.MEM_MODE, "1")

            # Verify the set command was called with proper formatting
            mock_command.assert_called_once()
            call_args = mock_command.call_args[0][0]
            assert "set" in str(call_args)

    @pytest.mark.asyncio
    async def test_set_command_with_boolean(self, siril_cli):
        with patch.object(siril_cli, "command") as mock_command:
            await siril_cli.set(SirilSetting.FORCE_16BIT, True)

            mock_command.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager_enter(self, siril_cli):
        with patch.object(siril_cli, "start") as mock_start:
            result = await siril_cli.__aenter__()

            mock_start.assert_called_once()
            assert result is siril_cli

    @pytest.mark.asyncio
    async def test_context_manager_exit(self, siril_cli):
        with patch.object(siril_cli, "command") as mock_command:
            await siril_cli.__aexit__(None, None, None)

            mock_command.assert_called_once()
            # Verify exit command was called
            call_args = mock_command.call_args[0][0]
            assert "exit" in str(call_args)

    @pytest.mark.asyncio
    async def test_manual_start_stop(self, siril_cli):
        with patch.object(siril_cli, "_start") as mock_start, patch.object(siril_cli, "_stop") as mock_stop:
            await siril_cli.start()
            mock_start.assert_called_once()

            await siril_cli.stop()
            mock_stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_startup_initialization_sequence(self, siril_cli):
        """Test the complete startup sequence with all initialization commands"""
        mock_process = Mock()
        mock_process.stdout = AsyncMock()
        mock_process.stderr = AsyncMock()

        # Mock resources with all limits set
        siril_cli._resources = SirilResource(
            cpu_limit=8,
            memory_limit="16384",  # type: ignore
            memory_percent=0.75,
        )

        with (
            patch("asyncio.create_subprocess_exec", return_value=mock_process),
            patch.object(siril_cli._consumer, "start"),
            patch.object(siril_cli._producer, "start"),
            patch.object(siril_cli._consumer, "siril_ready"),
            patch.object(siril_cli, "command") as mock_command,
            patch.object(siril_cli, "set") as mock_set,
            patch("asyncio.create_task"),
            patch.object(siril_cli, "_log_stream", new_callable=AsyncMock),
            patch.object(
                type(siril_cli._consumer), "pipe_path", new_callable=PropertyMock, return_value="/tmp/out_pipe"
            ),
            patch.object(
                type(siril_cli._producer), "pipe_path", new_callable=PropertyMock, return_value="/tmp/in_pipe"
            ),
        ):
            # Mock the ready future by making siril_ready a property that returns a completed future
            ready_future = asyncio.Future()
            ready_future.set_result(None)
            siril_cli._consumer.siril_ready = ready_future

            await siril_cli._start()

            # Verify initialization sequence
            assert mock_command.call_count >= 2  # requires + capabilities at minimum
            assert mock_set.call_count >= 3  # MEM_MODE, MEM_AMOUNT, MEM_RATIO

    def test_version_extraction(self, mock_siril_exe_exists):
        """Test version extraction from subprocess"""
        with (
            patch("subprocess.Popen") as mock_popen,
            patch.object(SirilCli, "_find_siril_cli", return_value="siril-cli"),
        ):
            mock_process = Mock()
            mock_process.communicate.return_value = (b"siril-cli 1.4.0-beta\n", b"")
            mock_popen.return_value = mock_process

            cli = SirilCli()

            assert cli.version == "siril-cli 1.4.0-beta"
            mock_popen.assert_called_once_with(["siril-cli", "--version"], stdout=subprocess.PIPE)

    @pytest.mark.asyncio
    async def test_integration_context_manager_flow(self, mock_subprocess_popen, mock_siril_exe_exists):
        """Test complete context manager flow"""

        with patch.object(SirilCli, "_find_siril_cli", return_value="siril-cli"):
            cli = SirilCli()

        # Mock all the async operations
        with patch.object(cli, "_start") as mock_start, patch.object(cli, "command") as mock_command:
            async with cli as siril:
                assert siril is cli
                # Could run commands here
                await siril.command("test_command")

            mock_start.assert_called_once()
            # Should have called exit command in __aexit__
            assert mock_command.call_count >= 2  # test_command + exit
