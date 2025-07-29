import pytest
import enum

from async_siril.command import CommandArgument, CommandFlag, CommandOptional, CommandOption, BaseCommand
from async_siril.command_types import stack_rejection, fits_extension


# Create a simple enum for testing
class ExampleEnum(enum.Enum):
    VALUE_ONE = "one"
    VALUE_TWO = "two"
    VALUE_THREE = "three"


class TestCommandArgument:
    def test_command_argument_creation_with_string(self):
        arg = CommandArgument("test_value")

        assert arg.value == "test_value"
        assert arg.valid is True
        assert str(arg) == "test_value"

    def test_command_argument_creation_with_number(self):
        arg = CommandArgument(42)

        assert arg.value == 42
        assert arg.valid is True
        assert str(arg) == "42"

    def test_command_argument_creation_with_float(self):
        arg = CommandArgument(3.14)

        assert arg.value == 3.14
        assert arg.valid is True
        assert str(arg) == "3.14"

    def test_command_argument_creation_with_none(self):
        arg = CommandArgument(None)

        assert arg.value is None
        assert arg.valid is False
        assert str(arg) == ""

    def test_command_argument_with_string_containing_spaces(self):
        arg = CommandArgument("value with spaces")

        assert arg.value == "value with spaces"
        assert arg.valid is True
        assert str(arg) == "'value with spaces'"

    def test_command_argument_with_enum(self):
        arg = CommandArgument(ExampleEnum.VALUE_ONE)

        assert arg.value == ExampleEnum.VALUE_ONE
        assert arg.valid is True
        assert str(arg) == "one"

    def test_command_argument_with_siril_enum(self):
        arg = CommandArgument(stack_rejection.REJECTION_SIGMA)

        assert arg.value == stack_rejection.REJECTION_SIGMA
        assert arg.valid is True
        assert str(arg) == "s"

    def test_command_argument_with_boolean_true(self):
        arg = CommandArgument(True)

        assert arg.value is True
        assert arg.valid is True
        assert str(arg) == "True"

    def test_command_argument_with_boolean_false(self):
        arg = CommandArgument(False)

        assert arg.value is False
        assert arg.valid is True  # False is still a valid value
        assert str(arg) == "False"

    def test_command_argument_with_zero(self):
        arg = CommandArgument(0)

        assert arg.value == 0
        assert arg.valid is True  # 0 is still a valid value
        assert str(arg) == "0"

    def test_command_argument_with_empty_string(self):
        arg = CommandArgument("")

        assert arg.value == ""
        assert arg.valid is True  # Empty string is still a valid value
        assert str(arg) == ""


class TestCommandFlag:
    def test_command_flag_creation_default(self):
        flag = CommandFlag("verbose")

        assert flag.name == "verbose"
        assert flag.value is True
        assert flag.valid is True
        assert str(flag) == "-verbose"

    def test_command_flag_creation_with_true(self):
        flag = CommandFlag("debug", True)

        assert flag.name == "debug"
        assert flag.value is True
        assert flag.valid is True
        assert str(flag) == "-debug"

    def test_command_flag_creation_with_false(self):
        flag = CommandFlag("quiet", False)

        assert flag.name == "quiet"
        assert flag.value is False
        assert flag.valid is False
        assert str(flag) == "-quiet"

    def test_command_flag_creation_with_none(self):
        flag = CommandFlag("option", None)

        assert flag.name == "option"
        assert flag.value is False  # None gets converted to False
        assert flag.valid is False
        assert str(flag) == "-option"

    def test_command_flag_with_hyphenated_name(self):
        flag = CommandFlag("multi-word")

        assert flag.name == "multi-word"
        assert flag.value is True
        assert flag.valid is True
        assert str(flag) == "-multi-word"

    def test_command_flag_with_empty_name(self):
        flag = CommandFlag("")

        assert flag.name == ""
        assert flag.value is True
        assert flag.valid is True
        assert str(flag) == "-"

    def test_command_flag_validity_only_true_when_value_true(self):
        flag_true = CommandFlag("test", True)
        flag_false = CommandFlag("test", False)
        flag_none = CommandFlag("test", None)

        assert flag_true.valid is True
        assert flag_false.valid is False
        assert flag_none.valid is False


class TestCommandOptional:
    def test_command_optional_creation_with_value(self):
        opt = CommandOptional("test_value")

        assert opt.value == "test_value"
        assert opt.valid is True
        assert str(opt) == "test_value"

    def test_command_optional_creation_with_none(self):
        opt = CommandOptional(None)

        assert opt.value is None
        assert opt.valid is False
        assert str(opt) == ""

    def test_command_optional_inherits_from_command_argument(self):
        opt = CommandOptional("value with spaces")

        # Should behave like CommandArgument for strings with spaces
        assert str(opt) == "'value with spaces'"

    def test_command_optional_with_enum(self):
        opt = CommandOptional(ExampleEnum.VALUE_TWO)

        assert opt.value == ExampleEnum.VALUE_TWO
        assert opt.valid is True
        assert str(opt) == "two"

    def test_command_optional_with_number(self):
        opt = CommandOptional(123)

        assert opt.value == 123
        assert opt.valid is True
        assert str(opt) == "123"

    def test_command_optional_with_zero(self):
        opt = CommandOptional(0)

        assert opt.value == 0
        assert opt.valid is True
        assert str(opt) == "0"

    def test_command_optional_with_false(self):
        opt = CommandOptional(False)

        assert opt.value is False
        assert opt.valid is True
        assert str(opt) == "False"


class TestCommandOption:
    def test_command_option_creation_with_value(self):
        option = CommandOption("output", "result.fits")

        assert option.name == "output"
        assert option.value == "result.fits"
        assert option.valid is True
        assert str(option) == "-output=result.fits"

    def test_command_option_creation_with_none(self):
        option = CommandOption("input", None)

        assert option.name == "input"
        assert option.value is None
        assert option.valid is False
        assert str(option) == ""

    def test_command_option_with_string_containing_spaces(self):
        option = CommandOption("file", "path with spaces.fits")

        assert option.name == "file"
        assert option.value == "path with spaces.fits"
        assert option.valid is True
        assert str(option) == "'-file=path with spaces.fits'"

    def test_command_option_with_number(self):
        option = CommandOption("threshold", 2.5)

        assert option.name == "threshold"
        assert option.value == 2.5
        assert option.valid is True
        assert str(option) == "-threshold=2.5"

    def test_command_option_with_integer(self):
        option = CommandOption("count", 42)

        assert option.name == "count"
        assert option.value == 42
        assert option.valid is True
        assert str(option) == "-count=42"

    def test_command_option_with_enum(self):
        option = CommandOption("method", ExampleEnum.VALUE_THREE)

        assert option.name == "method"
        assert option.value == ExampleEnum.VALUE_THREE
        assert option.valid is True
        assert str(option) == "-method=three"

    def test_command_option_with_siril_enum(self):
        option = CommandOption("extension", fits_extension.FITS_EXT_FITS)

        assert option.name == "extension"
        assert option.value == fits_extension.FITS_EXT_FITS
        assert option.valid is True
        assert str(option) == "-extension=fits"

    def test_command_option_with_boolean_true(self):
        option = CommandOption("enable", True)

        assert option.name == "enable"
        assert option.value is True
        assert option.valid is True
        assert str(option) == "-enable=True"

    def test_command_option_with_boolean_false(self):
        option = CommandOption("disable", False)

        assert option.name == "disable"
        assert option.value is False
        assert option.valid is True
        assert str(option) == "-disable=False"

    def test_command_option_with_zero(self):
        option = CommandOption("value", 0)

        assert option.name == "value"
        assert option.value == 0
        assert option.valid is True
        assert str(option) == "-value=0"

    def test_command_option_with_empty_string(self):
        option = CommandOption("empty", "")

        assert option.name == "empty"
        assert option.value == ""
        assert option.valid is True
        assert str(option) == "-empty="

    def test_command_option_with_hyphenated_name(self):
        option = CommandOption("multi-word", "value")

        assert option.name == "multi-word"
        assert option.value == "value"
        assert option.valid is True
        assert str(option) == "-multi-word=value"


class TestBaseCommand:
    def test_base_command_creation(self):
        command = BaseCommand()

        assert command.name == "BaseCommand"
        assert command.args == []
        assert command.valid is True
        assert str(command) == "BaseCommand"

    def test_base_command_name_from_class(self):
        # Create a subclass to test name generation
        class TestCommand(BaseCommand):
            pass

        command = TestCommand()

        assert command.name == "TestCommand"
        assert command.args == []
        assert command.valid is True
        assert str(command) == "TestCommand"

    def test_base_command_with_single_arg(self):
        command = BaseCommand()
        command.args = ["arg1"]

        assert str(command) == "BaseCommand arg1"

    def test_base_command_with_multiple_args(self):
        command = BaseCommand()
        command.args = ["arg1", "arg2", "arg3"]

        assert str(command) == "BaseCommand arg1 arg2 arg3"

    def test_base_command_with_empty_args_list(self):
        command = BaseCommand()
        command.args = []

        assert str(command) == "BaseCommand"

    def test_base_command_valid_always_true(self):
        command = BaseCommand()

        # Valid should always return True regardless of args
        assert command.valid is True

        command.args = ["arg1"]
        assert command.valid is True

        command.args = []
        assert command.valid is True

    def test_base_command_args_list_modification(self):
        command = BaseCommand()

        # Test that we can modify the args list
        command.args.append("new_arg")
        assert command.args == ["new_arg"]
        assert str(command) == "BaseCommand new_arg"

        command.args.extend(["arg2", "arg3"])
        assert command.args == ["new_arg", "arg2", "arg3"]
        assert str(command) == "BaseCommand new_arg arg2 arg3"

    def test_base_command_with_none_args(self):
        command = BaseCommand()
        command.args = [None, "valid_arg", None]

        # BaseCommand with None values in args raises TypeError
        # This is expected behavior as join() expects strings
        with pytest.raises(TypeError, match="sequence item 0: expected str instance, NoneType found"):
            str(command)

    def test_base_command_with_complex_args(self):
        command = BaseCommand()

        # Test with various argument types that could be string representations
        command.args = ["arg1", "123", "3.14", "true"]

        assert str(command) == "BaseCommand arg1 123 3.14 true"

    def test_base_command_inheritance_behavior(self):
        # Test that inheritance works properly
        class CustomCommand(BaseCommand):
            def __init__(self, custom_arg):
                super().__init__()
                self.custom_arg = custom_arg
                self.args = [custom_arg]

        command = CustomCommand("custom_value")

        assert command.name == "CustomCommand"
        assert command.custom_arg == "custom_value"
        assert command.args == ["custom_value"]
        assert str(command) == "CustomCommand custom_value"
        assert command.valid is True


class TestIntegrationScenarios:
    def test_command_objects_as_args(self):
        # Test how command objects might work together
        arg = CommandArgument("test_value")
        flag = CommandFlag("verbose")
        option = CommandOption("output", "result.fits")
        optional = CommandOptional("optional_value")

        # Test their string representations
        assert str(arg) == "test_value"
        assert str(flag) == "-verbose"
        assert str(option) == "-output=result.fits"
        assert str(optional) == "optional_value"

    def test_command_objects_validity(self):
        # Test validity across different objects
        valid_arg = CommandArgument("value")
        invalid_arg = CommandArgument(None)
        valid_flag = CommandFlag("flag", True)
        invalid_flag = CommandFlag("flag", False)
        valid_option = CommandOption("opt", "value")
        invalid_option = CommandOption("opt", None)
        valid_optional = CommandOptional("value")
        invalid_optional = CommandOptional(None)

        assert valid_arg.valid is True
        assert invalid_arg.valid is False
        assert valid_flag.valid is True
        assert invalid_flag.valid is False
        assert valid_option.valid is True
        assert invalid_option.valid is False
        assert valid_optional.valid is True
        assert invalid_optional.valid is False

    def test_edge_case_string_representations(self):
        # Test edge cases for string representations

        # CommandArgument with special characters
        arg_special = CommandArgument("path/with/slashes")
        assert str(arg_special) == "path/with/slashes"

        # CommandOption with special characters in value
        option_special = CommandOption("path", "folder/file name.fits")
        assert str(option_special) == "'-path=folder/file name.fits'"

        # CommandFlag with numeric name (edge case)
        flag_numeric = CommandFlag("123")
        assert str(flag_numeric) == "-123"

    def test_command_with_mixed_arg_types(self):
        # Test BaseCommand with different types of arguments
        command = BaseCommand()

        # Simulate how args might be populated with string representations
        arg = CommandArgument("input.fits")
        flag = CommandFlag("verbose")
        option = CommandOption("output", "result.fits")

        # In practice, these would be converted to strings when added to args
        command.args = [str(arg), str(flag), str(option)]

        expected = "BaseCommand input.fits -verbose -output=result.fits"
        assert str(command) == expected
