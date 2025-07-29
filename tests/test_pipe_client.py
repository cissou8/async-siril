import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from async_siril.event import PipeMode, PipeClient


class TestPipeMode:
    def test_pipe_mode_values(self):
        assert PipeMode.READ.value == "read"
        assert PipeMode.WRITE.value == "write"

    @patch("sys.platform", "darwin")
    def test_default_path_unix_read(self):
        mode = PipeMode.READ
        assert mode.default_path == "/tmp/siril_command.out"

    @patch("sys.platform", "darwin")
    def test_default_path_unix_write(self):
        mode = PipeMode.WRITE
        assert mode.default_path == "/tmp/siril_command.in"

    @patch("sys.platform", "linux")
    def test_default_path_linux_read(self):
        mode = PipeMode.READ
        assert mode.default_path == "/tmp/siril_command.out"

    @patch("sys.platform", "linux")
    def test_default_path_linux_write(self):
        mode = PipeMode.WRITE
        assert mode.default_path == "/tmp/siril_command.in"

    @patch("sys.platform", "win32")
    def test_default_path_windows_read(self):
        mode = PipeMode.READ
        assert mode.default_path == r"\\.\pipe\siril_command.out"

    @patch("sys.platform", "win32")
    def test_default_path_windows_write(self):
        mode = PipeMode.WRITE
        assert mode.default_path == r"\\.\pipe\siril_command.in"


class TestPipeClient:
    def test_pipe_client_init_read_mode(self):
        with patch("asyncio.get_event_loop") as mock_get_loop:
            mock_loop = MagicMock()
            mock_get_loop.return_value = mock_loop

            client = PipeClient(PipeMode.READ)

            assert client.mode == PipeMode.READ
            assert client.encoding == "utf-8"
            assert client._file is None
            assert client.path == PipeMode.READ.default_path
            assert client._loop == mock_loop

    def test_pipe_client_init_write_mode(self):
        with patch("asyncio.get_event_loop") as mock_get_loop:
            mock_loop = MagicMock()
            mock_get_loop.return_value = mock_loop

            client = PipeClient(PipeMode.WRITE)

            assert client.mode == PipeMode.WRITE
            assert client.encoding == "utf-8"
            assert client._file is None
            assert client.path == PipeMode.WRITE.default_path

    def test_pipe_client_init_custom_encoding(self):
        with patch("asyncio.get_event_loop") as mock_get_loop:
            mock_loop = MagicMock()
            mock_get_loop.return_value = mock_loop

            client = PipeClient(PipeMode.READ, encoding="latin-1")

            assert client.encoding == "latin-1"

    @patch("sys.platform", "darwin")
    def test_is_windows_property_false(self):
        with patch("asyncio.get_event_loop"):
            client = PipeClient(PipeMode.READ)
            assert client._is_windows is False

    @patch("sys.platform", "win32")
    def test_is_windows_property_true(self):
        with patch("asyncio.get_event_loop"):
            client = PipeClient(PipeMode.READ)
            assert client._is_windows is True

    @patch("sys.platform", "darwin")
    def test_is_binary_property_false_unix(self):
        with patch("asyncio.get_event_loop"):
            client = PipeClient(PipeMode.READ)
            assert client._is_binary is False

    @patch("sys.platform", "win32")
    def test_is_binary_property_true_windows(self):
        with patch("asyncio.get_event_loop"):
            client = PipeClient(PipeMode.READ)
            assert client._is_binary is True

    @patch("sys.platform", "darwin")
    def test_open_mode_read_unix(self):
        with patch("asyncio.get_event_loop"):
            client = PipeClient(PipeMode.READ)
            assert client._open_mode == "r"

    @patch("sys.platform", "darwin")
    def test_open_mode_write_unix(self):
        with patch("asyncio.get_event_loop"):
            client = PipeClient(PipeMode.WRITE)
            assert client._open_mode == "w"

    @patch("sys.platform", "win32")
    def test_open_mode_read_windows(self):
        with patch("asyncio.get_event_loop"):
            client = PipeClient(PipeMode.READ)
            assert client._open_mode == "rb"

    @patch("sys.platform", "win32")
    def test_open_mode_write_windows(self):
        with patch("asyncio.get_event_loop"):
            client = PipeClient(PipeMode.WRITE)
            assert client._open_mode == "wb"

    def test_close_with_no_file(self):
        with patch("asyncio.get_event_loop"):
            client = PipeClient(PipeMode.READ)
            # Should not raise an error
            client.close()
            assert client._file is None

    def test_close_with_file(self):
        with patch("asyncio.get_event_loop"):
            client = PipeClient(PipeMode.READ)
            mock_file = MagicMock()
            client._file = mock_file

            client.close()

            mock_file.close.assert_called_once()
            assert client._file is None

    @pytest.mark.asyncio
    @patch("sys.platform", "darwin")
    @patch("os.path.exists")
    @patch("asyncio.to_thread")
    async def test_connect_unix_success(self, mock_to_thread, mock_exists):
        mock_exists.return_value = True
        mock_file = MagicMock()
        mock_to_thread.return_value = mock_file

        with patch("asyncio.get_event_loop"):
            client = PipeClient(PipeMode.READ)
            await client.connect()

            mock_exists.assert_called_with(client.path)
            mock_to_thread.assert_called_once_with(open, client.path, "r", encoding="utf-8")
            assert client._file == mock_file

    @pytest.mark.asyncio
    @patch("sys.platform", "darwin")
    @patch("os.path.exists")
    @patch("asyncio.sleep")
    @patch("asyncio.to_thread")
    async def test_connect_unix_wait_for_file(self, mock_to_thread, mock_sleep, mock_exists):
        # First call returns False, second returns True
        mock_exists.side_effect = [False, True]
        mock_file = MagicMock()
        mock_to_thread.return_value = mock_file

        with patch("asyncio.get_event_loop"):
            client = PipeClient(PipeMode.READ)
            await client.connect()

            assert mock_exists.call_count == 2
            mock_sleep.assert_called_once_with(0.1)
            assert client._file == mock_file

    @pytest.mark.asyncio
    @patch("sys.platform", "win32")
    @patch("asyncio.to_thread")
    async def test_connect_windows_success(self, mock_to_thread):
        mock_file = MagicMock()
        mock_to_thread.return_value = mock_file

        with patch("asyncio.get_event_loop"):
            client = PipeClient(PipeMode.READ)
            await client.connect()

            mock_to_thread.assert_called_once_with(open, client.path, "rb", buffering=0)
            assert client._file == mock_file

    @pytest.mark.asyncio
    @patch("sys.platform", "win32")
    @patch("asyncio.to_thread")
    @patch("asyncio.sleep")
    async def test_connect_windows_retry(self, mock_sleep, mock_to_thread):
        mock_file = MagicMock()
        # First call raises FileNotFoundError, second succeeds
        mock_to_thread.side_effect = [FileNotFoundError(), mock_file]

        with patch("asyncio.get_event_loop"):
            client = PipeClient(PipeMode.READ)
            await client.connect()

            assert mock_to_thread.call_count == 2
            mock_sleep.assert_called_once_with(0.1)
            assert client._file == mock_file

    @pytest.mark.asyncio
    async def test_write_line_wrong_mode(self):
        with patch("asyncio.get_event_loop"):
            client = PipeClient(PipeMode.READ)

            with pytest.raises(RuntimeError, match="Pipe not in write mode"):
                await client.write_line("test message")

    @pytest.mark.asyncio
    async def test_write_line_not_connected(self):
        with patch("asyncio.get_event_loop"):
            client = PipeClient(PipeMode.WRITE)

            with pytest.raises(RuntimeError, match="Pipe not connected"):
                await client.write_line("test message")

    @pytest.mark.asyncio
    @patch("sys.platform", "darwin")
    async def test_write_line_unix(self):
        with patch("asyncio.get_event_loop"):
            client = PipeClient(PipeMode.WRITE)
            mock_file = MagicMock()
            client._file = mock_file

            with patch.object(client._loop, "run_in_executor", new_callable=AsyncMock) as mock_executor:
                mock_executor.return_value = None

                await client.write_line("test message")

                # Should be called twice: once for write, once for flush
                assert mock_executor.call_count == 2
                mock_executor.assert_any_call(None, mock_file.write, "test message\n")
                mock_executor.assert_any_call(None, mock_file.flush)

    @pytest.mark.asyncio
    @patch("sys.platform", "win32")
    async def test_write_line_windows(self):
        with patch("asyncio.get_event_loop"):
            client = PipeClient(PipeMode.WRITE)
            mock_file = MagicMock()
            client._file = mock_file

            with patch.object(client._loop, "run_in_executor", new_callable=AsyncMock) as mock_executor:
                mock_executor.return_value = None

                await client.write_line("test message")

                # Should be called twice: once for write, once for flush
                assert mock_executor.call_count == 2
                mock_executor.assert_any_call(None, mock_file.write, b"test message\n")
                mock_executor.assert_any_call(None, mock_file.flush)

    @pytest.mark.asyncio
    async def test_read_line_wrong_mode(self):
        with patch("asyncio.get_event_loop"):
            client = PipeClient(PipeMode.WRITE)

            with pytest.raises(RuntimeError, match="Pipe not in read mode"):
                await client.read_line()

    @pytest.mark.asyncio
    async def test_read_line_not_connected(self):
        with patch("asyncio.get_event_loop"):
            client = PipeClient(PipeMode.READ)

            with pytest.raises(RuntimeError, match="Pipe not connected"):
                await client.read_line()

    @pytest.mark.asyncio
    @patch("sys.platform", "darwin")
    async def test_read_line_unix(self):
        with patch("asyncio.get_event_loop"):
            client = PipeClient(PipeMode.READ)
            mock_file = MagicMock()
            client._file = mock_file

            with patch.object(client._loop, "run_in_executor", new_callable=AsyncMock) as mock_executor:
                mock_executor.return_value = "test message\n"

                result = await client.read_line()

                assert result == "test message"
                mock_executor.assert_called_once_with(None, mock_file.readline)

    @pytest.mark.asyncio
    @patch("sys.platform", "win32")
    async def test_read_line_windows_bytes(self):
        with patch("asyncio.get_event_loop"):
            client = PipeClient(PipeMode.READ)
            mock_file = MagicMock()
            client._file = mock_file

            with patch.object(client._loop, "run_in_executor", new_callable=AsyncMock) as mock_executor:
                mock_executor.return_value = b"test message\n"

                result = await client.read_line()

                assert result == "test message"
                mock_executor.assert_called_once_with(None, mock_file.readline)

    @pytest.mark.asyncio
    @patch("sys.platform", "darwin")
    async def test_read_line_with_custom_encoding(self):
        with patch("asyncio.get_event_loop"):
            client = PipeClient(PipeMode.READ, encoding="latin-1")
            mock_file = MagicMock()
            client._file = mock_file

            with patch.object(client._loop, "run_in_executor", new_callable=AsyncMock) as mock_executor:
                mock_executor.return_value = "test message\n"

                result = await client.read_line()

                assert result == "test message"

    @pytest.mark.asyncio
    @patch("sys.platform", "win32")
    async def test_read_line_windows_custom_encoding(self):
        with patch("asyncio.get_event_loop"):
            client = PipeClient(PipeMode.READ, encoding="latin-1")
            mock_file = MagicMock()
            client._file = mock_file

            with patch.object(client._loop, "run_in_executor", new_callable=AsyncMock) as mock_executor:
                # Simulate bytes being returned
                test_bytes = "test message\n".encode("latin-1")
                mock_executor.return_value = test_bytes

                result = await client.read_line()

                assert result == "test message"

    @pytest.mark.asyncio
    @patch("sys.platform", "darwin")
    async def test_read_line_empty_string(self):
        with patch("asyncio.get_event_loop"):
            client = PipeClient(PipeMode.READ)
            mock_file = MagicMock()
            client._file = mock_file

            with patch.object(client._loop, "run_in_executor", new_callable=AsyncMock) as mock_executor:
                mock_executor.return_value = ""

                result = await client.read_line()

                assert result == ""

    @pytest.mark.asyncio
    @patch("sys.platform", "win32")
    async def test_write_line_custom_encoding(self):
        with patch("asyncio.get_event_loop"):
            client = PipeClient(PipeMode.WRITE, encoding="latin-1")
            mock_file = MagicMock()
            client._file = mock_file

            with patch.object(client._loop, "run_in_executor", new_callable=AsyncMock) as mock_executor:
                mock_executor.return_value = None

                await client.write_line("test message")

                expected_bytes = "test message\n".encode("latin-1")
                mock_executor.assert_any_call(None, mock_file.write, expected_bytes)
