from unittest.mock import patch
from async_siril.resources import SirilResource


class TestSirilResource:
    def test_siril_resource_default_initialization(self):
        resource = SirilResource()

        assert resource.cpu_limit is None
        assert resource.memory_limit is None
        assert resource.memory_percent == 0.9

    def test_siril_resource_custom_initialization(self):
        resource = SirilResource(cpu_limit=4, memory_limit="8.0", memory_percent=0.75)

        assert resource.cpu_limit == 4
        assert resource.memory_limit == "8.0"
        assert resource.memory_percent == 0.75

    def test_siril_resource_partial_initialization(self):
        resource = SirilResource(cpu_limit=2)

        assert resource.cpu_limit == 2
        assert resource.memory_limit is None
        assert resource.memory_percent == 0.9

    def test_siril_resource_memory_limit_only(self):
        resource = SirilResource(memory_limit="16.0")

        assert resource.cpu_limit is None
        assert resource.memory_limit == "16.0"
        assert resource.memory_percent == 0.9

    def test_siril_resource_memory_percent_only(self):
        resource = SirilResource(memory_percent=0.8)

        assert resource.cpu_limit is None
        assert resource.memory_limit is None
        assert resource.memory_percent == 0.8

    def test_siril_resource_zero_values(self):
        resource = SirilResource(cpu_limit=0, memory_limit="0.0", memory_percent=0.0)

        assert resource.cpu_limit == 0
        assert resource.memory_limit == "0.0"
        assert resource.memory_percent == 0.0

    def test_siril_resource_negative_values(self):
        resource = SirilResource(cpu_limit=-1, memory_percent=-0.1)

        assert resource.cpu_limit == -1
        assert resource.memory_percent == -0.1

    def test_siril_resource_float_memory_percent(self):
        resource = SirilResource(memory_percent=0.95)

        assert resource.memory_percent == 0.95

    def test_siril_resource_string_memory_limit(self):
        resource = SirilResource(memory_limit="12.5")

        assert resource.memory_limit == "12.5"

    @patch("async_siril.resources.container_aware_cpu_limit")
    @patch("async_siril.resources.container_aware_memory_limit_gb")
    def test_container_aware_limits(self, mock_memory_limit, mock_cpu_limit):
        mock_cpu_limit.return_value = 2
        mock_memory_limit.return_value = "4.0"

        resource = SirilResource.container_aware_limits()

        assert resource.cpu_limit == 2
        assert resource.memory_limit == "4.0"
        assert resource.memory_percent == 0.9  # Default value

        mock_cpu_limit.assert_called_once()
        mock_memory_limit.assert_called_once()

    @patch("async_siril.resources.container_aware_cpu_limit")
    @patch("async_siril.resources.container_aware_memory_limit_gb")
    def test_container_aware_limits_none_values(self, mock_memory_limit, mock_cpu_limit):
        mock_cpu_limit.return_value = None
        mock_memory_limit.return_value = None

        resource = SirilResource.container_aware_limits()

        assert resource.cpu_limit is None
        assert resource.memory_limit is None
        assert resource.memory_percent == 0.9

    @patch("async_siril.resources.container_aware_cpu_limit")
    @patch("async_siril.resources.container_aware_memory_limit_gb")
    def test_container_aware_limits_partial_values(self, mock_memory_limit, mock_cpu_limit):
        mock_cpu_limit.return_value = 8
        mock_memory_limit.return_value = None

        resource = SirilResource.container_aware_limits()

        assert resource.cpu_limit == 8
        assert resource.memory_limit is None
        assert resource.memory_percent == 0.9

    def test_default_limits(self):
        resource = SirilResource.default_limits()

        assert resource.cpu_limit is None
        assert resource.memory_limit is None
        assert resource.memory_percent == 0.9

    def test_dataclass_equality(self):
        resource1 = SirilResource(cpu_limit=4, memory_limit="8.0", memory_percent=0.8)
        resource2 = SirilResource(cpu_limit=4, memory_limit="8.0", memory_percent=0.8)
        resource3 = SirilResource(cpu_limit=2, memory_limit="8.0", memory_percent=0.8)

        assert resource1 == resource2
        assert resource1 != resource3

    def test_dataclass_repr(self):
        resource = SirilResource(cpu_limit=4, memory_limit="8.0", memory_percent=0.8)
        repr_str = repr(resource)

        assert "SirilResource" in repr_str
        assert "cpu_limit=4" in repr_str
        assert "memory_limit='8.0'" in repr_str
        assert "memory_percent=0.8" in repr_str

    def test_dataclass_fields_exist(self):
        resource = SirilResource()

        # Test that the dataclass has the expected fields
        assert hasattr(resource, "cpu_limit")
        assert hasattr(resource, "memory_limit")
        assert hasattr(resource, "memory_percent")

    def test_static_method_independence(self):
        # Test that static methods don't interfere with each other
        default = SirilResource.default_limits()

        with patch("async_siril.resources.container_aware_cpu_limit", return_value=16):
            with patch("async_siril.resources.container_aware_memory_limit_gb", return_value="32.0"):
                container = SirilResource.container_aware_limits()

        assert default.cpu_limit is None
        assert default.memory_limit is None
        assert container.cpu_limit == 16
        assert container.memory_limit == "32.0"

    def test_type_annotations(self):
        # Test that the class works with different types as expected
        resource = SirilResource(cpu_limit=None, memory_limit=None, memory_percent=1.0)

        assert resource.cpu_limit is None
        assert resource.memory_limit is None
        assert resource.memory_percent == 1.0

    def test_memory_percent_edge_cases(self):
        # Test edge cases for memory_percent
        resource_high = SirilResource(memory_percent=1.0)
        resource_low = SirilResource(memory_percent=0.1)
        resource_zero = SirilResource(memory_percent=0.0)

        assert resource_high.memory_percent == 1.0
        assert resource_low.memory_percent == 0.1
        assert resource_zero.memory_percent == 0.0

    def test_large_values(self):
        # Test with large values
        resource = SirilResource(
            cpu_limit=1000,
            memory_limit="999.99",
            memory_percent=10.0,  # Over 100%
        )

        assert resource.cpu_limit == 1000
        assert resource.memory_limit == "999.99"
        assert resource.memory_percent == 10.0

    @patch("async_siril.resources.container_aware_cpu_limit")
    @patch("async_siril.resources.container_aware_memory_limit_gb")
    def test_container_aware_limits_function_calls(self, mock_memory_limit, mock_cpu_limit):
        # Test that the functions are called exactly once per call to container_aware_limits
        mock_cpu_limit.return_value = 1
        mock_memory_limit.return_value = "1.0"

        # First call
        resource1 = SirilResource.container_aware_limits()
        assert mock_cpu_limit.call_count == 1
        assert mock_memory_limit.call_count == 1

        # Second call
        resource2 = SirilResource.container_aware_limits()
        assert mock_cpu_limit.call_count == 2
        assert mock_memory_limit.call_count == 2

        # Both should have the same values but be different objects
        assert resource1.cpu_limit == resource2.cpu_limit
        assert resource1.memory_limit == resource2.memory_limit
        assert resource1 is not resource2
