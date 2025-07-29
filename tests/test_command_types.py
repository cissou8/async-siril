import pytest

from async_siril.command import SequenceFilter, CommandOption, CommandFlag
from async_siril.command_types import sequence_filter_type


class TestSequenceFilter:
    def test_sequence_filter_creation_with_value(self):
        filter_obj = SequenceFilter(sequence_filter_type.FILTER_FWHM, value=2.5)

        assert filter_obj.filter_type == sequence_filter_type.FILTER_FWHM
        assert filter_obj.value == 2.5
        assert filter_obj.percent is None

    def test_sequence_filter_creation_with_percent(self):
        filter_obj = SequenceFilter(sequence_filter_type.FILTER_QUALITY, percent=80.0)

        assert filter_obj.filter_type == sequence_filter_type.FILTER_QUALITY
        assert filter_obj.value is None
        assert filter_obj.percent == 80.0

    def test_sequence_filter_creation_inclusion_type(self):
        filter_obj = SequenceFilter(sequence_filter_type.FILTER_INCLUSION)

        assert filter_obj.filter_type == sequence_filter_type.FILTER_INCLUSION
        assert filter_obj.value is None
        assert filter_obj.percent is None

    def test_sequence_filter_creation_with_both_value_and_percent_raises_error(self):
        with pytest.raises(ValueError, match="A filter must either have a value or percent argument"):
            SequenceFilter(sequence_filter_type.FILTER_FWHM, value=2.5, percent=80.0)

    def test_sequence_filter_creation_with_neither_value_nor_percent_raises_error(self):
        with pytest.raises(ValueError, match="A filter must either have a value or percent argument"):
            SequenceFilter(sequence_filter_type.FILTER_ROUNDNESS)

    def test_sequence_filter_inclusion_allows_no_parameters(self):
        # FILTER_INCLUSION should not raise an error when no value or percent is provided
        filter_obj = SequenceFilter(sequence_filter_type.FILTER_INCLUSION)

        assert filter_obj.filter_type == sequence_filter_type.FILTER_INCLUSION
        assert filter_obj.value is None
        assert filter_obj.percent is None

    def test_filter_parameter_returns_flag_for_inclusion(self):
        filter_obj = SequenceFilter(sequence_filter_type.FILTER_INCLUSION)
        result = filter_obj.filter_parameter()

        assert isinstance(result, CommandFlag)
        assert result.name == "filter-incl"
        assert result.valid is True

    def test_filter_parameter_returns_option_with_value(self):
        filter_obj = SequenceFilter(sequence_filter_type.FILTER_FWHM, value=3.2)
        result = filter_obj.filter_parameter()

        assert isinstance(result, CommandOption)
        assert result.name == "filter-fwhm"
        assert result.value == "3.2"
        assert result.valid is True

    def test_filter_parameter_returns_option_with_percent(self):
        filter_obj = SequenceFilter(sequence_filter_type.FILTER_BACKGROUND, percent=25.5)
        result = filter_obj.filter_parameter()

        assert isinstance(result, CommandOption)
        assert result.name == "filter-bkg"
        assert result.value == "25.5%"
        assert result.valid is True

    def test_filter_parameter_with_integer_value(self):
        filter_obj = SequenceFilter(sequence_filter_type.FILTER_STAR_COUNT, value=50)
        result = filter_obj.filter_parameter()

        assert isinstance(result, CommandOption)
        assert result.name == "filter-nbstars"
        assert result.value == "50"
        assert result.valid is True

    def test_filter_parameter_with_zero_value(self):
        filter_obj = SequenceFilter(sequence_filter_type.FILTER_FWHM, value=0.0)
        result = filter_obj.filter_parameter()

        assert isinstance(result, CommandOption)
        assert result.name == "filter-fwhm"
        assert result.value == "0.0"
        assert result.valid is True

    def test_filter_parameter_with_zero_percent(self):
        filter_obj = SequenceFilter(sequence_filter_type.FILTER_QUALITY, percent=0.0)
        result = filter_obj.filter_parameter()

        assert isinstance(result, CommandOption)
        assert result.name == "filter-quality"
        assert result.value == "0.0%"
        assert result.valid is True

    def test_filter_parameter_with_negative_value(self):
        filter_obj = SequenceFilter(sequence_filter_type.FILTER_ROUNDNESS, value=-1.5)
        result = filter_obj.filter_parameter()

        assert isinstance(result, CommandOption)
        assert result.name == "filter-round"
        assert result.value == "-1.5"
        assert result.valid is True

    def test_filter_parameter_with_negative_percent(self):
        filter_obj = SequenceFilter(sequence_filter_type.FILTER_WFWHM, percent=-10.0)
        result = filter_obj.filter_parameter()

        assert isinstance(result, CommandOption)
        assert result.name == "filter-wfwhm"
        assert result.value == "-10.0%"
        assert result.valid is True

    def test_all_filter_types_with_value(self):
        # Test all non-inclusion filter types with a value
        filter_types = [
            sequence_filter_type.FILTER_FWHM,
            sequence_filter_type.FILTER_WFWHM,
            sequence_filter_type.FILTER_ROUNDNESS,
            sequence_filter_type.FILTER_QUALITY,
            sequence_filter_type.FILTER_BACKGROUND,
            sequence_filter_type.FILTER_STAR_COUNT,
        ]

        for filter_type in filter_types:
            filter_obj = SequenceFilter(filter_type, value=1.0)
            result = filter_obj.filter_parameter()

            assert isinstance(result, CommandOption)
            assert result.name == filter_type.value
            assert result.value == "1.0"
            assert result.valid is True

    def test_all_filter_types_with_percent(self):
        # Test all non-inclusion filter types with a percent
        filter_types = [
            sequence_filter_type.FILTER_FWHM,
            sequence_filter_type.FILTER_WFWHM,
            sequence_filter_type.FILTER_ROUNDNESS,
            sequence_filter_type.FILTER_QUALITY,
            sequence_filter_type.FILTER_BACKGROUND,
            sequence_filter_type.FILTER_STAR_COUNT,
        ]

        for filter_type in filter_types:
            filter_obj = SequenceFilter(filter_type, percent=50.0)
            result = filter_obj.filter_parameter()

            assert isinstance(result, CommandOption)
            assert result.name == filter_type.value
            assert result.value == "50.0%"
            assert result.valid is True

    def test_filter_none_type_with_value(self):
        # Test FILTER_NONE (empty string) with value
        filter_obj = SequenceFilter(sequence_filter_type.FILTER_NONE, value=2.0)
        result = filter_obj.filter_parameter()

        assert isinstance(result, CommandOption)
        assert result.name == ""
        assert result.value == "2.0"
        assert result.valid is True

    def test_filter_none_type_with_percent(self):
        # Test FILTER_NONE (empty string) with percent
        filter_obj = SequenceFilter(sequence_filter_type.FILTER_NONE, percent=75.0)
        result = filter_obj.filter_parameter()

        assert isinstance(result, CommandOption)
        assert result.name == ""
        assert result.value == "75.0%"
        assert result.valid is True

    def test_large_values_and_percents(self):
        # Test with large values
        filter_obj = SequenceFilter(sequence_filter_type.FILTER_FWHM, value=999999.99)
        result = filter_obj.filter_parameter()
        assert result.value == "999999.99"

        # Test with large percent
        filter_obj = SequenceFilter(sequence_filter_type.FILTER_QUALITY, percent=100.0)
        result = filter_obj.filter_parameter()
        assert result.value == "100.0%"

    def test_very_small_values_and_percents(self):
        # Test with very small values
        filter_obj = SequenceFilter(sequence_filter_type.FILTER_ROUNDNESS, value=0.001)
        result = filter_obj.filter_parameter()
        assert result.value == "0.001"

        # Test with very small percent
        filter_obj = SequenceFilter(sequence_filter_type.FILTER_BACKGROUND, percent=0.01)
        result = filter_obj.filter_parameter()
        assert result.value == "0.01%"

    def test_sequence_filter_attributes_immutable_after_creation(self):
        # Test that the filter maintains its attributes correctly
        filter_obj = SequenceFilter(sequence_filter_type.FILTER_QUALITY, value=5.5)

        # Verify initial state
        assert filter_obj.filter_type == sequence_filter_type.FILTER_QUALITY
        assert filter_obj.value == 5.5
        assert filter_obj.percent is None

        # Call filter_parameter multiple times and ensure attributes don't change
        result1 = filter_obj.filter_parameter()
        result2 = filter_obj.filter_parameter()

        assert filter_obj.filter_type == sequence_filter_type.FILTER_QUALITY
        assert filter_obj.value == 5.5
        assert filter_obj.percent is None

        # Results should be consistent
        assert result1.name == result2.name
        assert result1.value == result2.value

    def test_edge_case_inclusion_with_value_and_percent_allowed(self):
        # FILTER_INCLUSION should allow value and percent parameters without raising errors
        # but they should be ignored in filter_parameter()
        filter_obj = SequenceFilter(sequence_filter_type.FILTER_INCLUSION, value=10.0, percent=50.0)

        assert filter_obj.filter_type == sequence_filter_type.FILTER_INCLUSION
        assert filter_obj.value == 10.0
        assert filter_obj.percent == 50.0

        result = filter_obj.filter_parameter()
        assert isinstance(result, CommandFlag)
        assert result.name == "filter-incl"

    def test_string_representation_compatibility(self):
        # Test that the results from filter_parameter() work with string conversion
        value_filter = SequenceFilter(sequence_filter_type.FILTER_FWHM, value=2.5)
        value_result = value_filter.filter_parameter()
        assert str(value_result) == "-filter-fwhm=2.5"

        percent_filter = SequenceFilter(sequence_filter_type.FILTER_QUALITY, percent=80.0)
        percent_result = percent_filter.filter_parameter()
        assert str(percent_result) == "-filter-quality=80.0%"

        inclusion_filter = SequenceFilter(sequence_filter_type.FILTER_INCLUSION)
        inclusion_result = inclusion_filter.filter_parameter()
        assert str(inclusion_result) == "-filter-incl"
