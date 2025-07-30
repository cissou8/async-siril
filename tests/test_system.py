import pytest
import os
import tempfile
from unittest.mock import patch, mock_open, MagicMock

from async_siril.system import (
    human_readable_byte_size,
    available_memory,
    memory_used,
    process_info,
    container_aware_memory_limit_gb,
    container_aware_cpu_limit,
    read_int,
)


class TestHumanReadableByteSize:
    def test_bytes(self):
        result = human_readable_byte_size(512)
        assert result == "512.000 B"

    def test_kilobytes(self):
        result = human_readable_byte_size(1024)
        assert result == "1.000 KiB"

    def test_megabytes(self):
        result = human_readable_byte_size(1024 * 1024)
        assert result == "1.000 MiB"

    def test_gigabytes(self):
        result = human_readable_byte_size(1024 * 1024 * 1024)
        assert result == "1.000 GiB"

    def test_terabytes(self):
        result = human_readable_byte_size(1024 * 1024 * 1024 * 1024)
        assert result == "1.000 TiB"

    def test_zero_bytes(self):
        result = human_readable_byte_size(0)
        assert result == "0.000 B"

    def test_negative_bytes(self):
        result = human_readable_byte_size(-1024)
        assert result == "-1.000 KiB"

    def test_fractional_kilobytes(self):
        result = human_readable_byte_size(1536)  # 1.5 KB
        assert result == "1.500 KiB"

    def test_very_large_number(self):
        huge_number = 1024**8
        result = human_readable_byte_size(huge_number)
        assert "YiB" in result


class TestAvailableMemory:
    @patch("async_siril.system.psutil.virtual_memory")
    def test_available_memory(self, mock_virtual_memory):
        mock_virtual_memory.return_value.available = 8589934592  # 8GB
        result = available_memory()
        assert result == 8589934592


class TestMemoryUsed:
    @patch("async_siril.system.psutil.Process")
    def test_memory_used(self, mock_process_class):
        mock_process = MagicMock()
        mock_process.memory_info.return_value.rss = 1073741824  # 1GB
        mock_process_class.return_value = mock_process

        result = memory_used()
        assert isinstance(result, str)
        assert "1.0G" in result


class TestProcessInfo:
    @patch("async_siril.system.psutil.Process")
    def test_process_info(self, mock_process_class):
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_process.name.return_value = "python"
        mock_process.status.return_value = "running"
        mock_process.memory_info.return_value.rss = 1073741824  # 1GB
        mock_process_class.return_value = mock_process

        result = process_info()

        assert result["pid"] == 12345
        assert result["name"] == "python"
        assert result["status"] == "running"
        assert isinstance(result["rss"], str)
        assert "1.0G" in result["rss"]


class TestReadInt:
    def test_read_int_file_exists_valid_content(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("12345\n")
            temp_file = f.name

        try:
            result = read_int(temp_file)
            assert result == 12345
        finally:
            os.unlink(temp_file)

    def test_read_int_file_exists_invalid_content(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("not_a_number\n")
            temp_file = f.name

        try:
            result = read_int(temp_file)
            assert result is None
        finally:
            os.unlink(temp_file)

    def test_read_int_file_does_not_exist(self):
        result = read_int("/nonexistent/file")
        assert result is None

    def test_read_int_empty_file(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            temp_file = f.name

        try:
            result = read_int(temp_file)
            assert result is None
        finally:
            os.unlink(temp_file)

    def test_read_int_negative_number(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("-12345\n")
            temp_file = f.name

        try:
            result = read_int(temp_file)
            assert result == -12345
        finally:
            os.unlink(temp_file)


class TestContainerAwareMemoryLimitGb:
    @patch("async_siril.system.read_int")
    def test_memory_limit_found_first_path(self, mock_read_int):
        mock_read_int.side_effect = [2147483648, None, None, None, None, None, None]  # 2GB

        result = container_aware_memory_limit_gb()
        assert result == "2.00"

    @patch("async_siril.system.read_int")
    def test_memory_limit_found_later_path(self, mock_read_int):
        mock_read_int.side_effect = [None, None, None, 4294967296, None, None, None]  # 4GB

        result = container_aware_memory_limit_gb()
        assert result == "4.00"

    @patch("async_siril.system.read_int")
    def test_memory_limit_not_found(self, mock_read_int):
        mock_read_int.return_value = None

        result = container_aware_memory_limit_gb()
        assert result is None

    @patch("async_siril.system.read_int")
    def test_memory_limit_zero_value(self, mock_read_int):
        mock_read_int.return_value = 0

        result = container_aware_memory_limit_gb()
        assert result is None

    @patch("async_siril.system.read_int")
    def test_memory_limit_negative_value(self, mock_read_int):
        mock_read_int.return_value = -1

        result = container_aware_memory_limit_gb()
        assert result is None


class TestContainerAwareCpuLimit:
    @patch("async_siril.system.os.path.exists")
    @patch("async_siril.system.read_int")
    def test_cgroup1_cpu_limit_found(self, mock_read_int, mock_exists):
        mock_exists.side_effect = lambda path: path in [
            "/sys/fs/cgroup/cpu/cpu.cfs_quota_us",
            "/sys/fs/cgroup/cpu/cpu.cfs_period_us",
        ]
        mock_read_int.side_effect = [200000, 100000]  # 2 CPUs

        result = container_aware_cpu_limit()
        assert result == 2

    @patch("async_siril.system.os.path.exists")
    @patch("async_siril.system.read_int")
    def test_cgroup1_cpu_limit_no_quota(self, mock_read_int, mock_exists):
        mock_exists.side_effect = lambda path: path in [
            "/sys/fs/cgroup/cpu/cpu.cfs_quota_us",
            "/sys/fs/cgroup/cpu/cpu.cfs_period_us",
        ]
        mock_read_int.side_effect = [None, 100000]

        result = container_aware_cpu_limit()
        assert result is None

    @patch("async_siril.system.os.path.exists")
    def test_cgroup2_cpu_limit_found(self, mock_exists):
        mock_exists.side_effect = lambda path: path == "/sys/fs/cgroup/cpu.max"

        with patch("builtins.open", mock_open(read_data="300000 100000\n")):
            result = container_aware_cpu_limit()
            assert result == 3

    @patch("async_siril.system.os.path.exists")
    def test_cgroup2_cpu_limit_invalid_format(self, mock_exists):
        mock_exists.side_effect = lambda path: path == "/sys/fs/cgroup/cpu.max"

        with patch("builtins.open", mock_open(read_data="invalid format\n")):
            result = container_aware_cpu_limit()
            assert result is None

    @patch("async_siril.system.os.path.exists")
    def test_cgroup2_cpu_limit_single_value(self, mock_exists):
        mock_exists.side_effect = lambda path: path == "/sys/fs/cgroup/cpu.max"

        with patch("builtins.open", mock_open(read_data="300000\n")):
            result = container_aware_cpu_limit()
            assert result is None

    @patch("async_siril.system.os.path.exists")
    def test_no_cgroup_files_found(self, mock_exists):
        mock_exists.return_value = False

        result = container_aware_cpu_limit()
        assert result is None

    @patch("async_siril.system.os.path.exists")
    def test_cgroup2_file_read_error(self, mock_exists):
        mock_exists.side_effect = lambda path: path == "/sys/fs/cgroup/cpu.max"

        with patch("builtins.open", side_effect=OSError("File read error")):
            with pytest.raises(OSError):
                container_aware_cpu_limit()
