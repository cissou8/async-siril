from async_siril.event import SirilEvent


class TestSirilEvent:
    def test_status_event_parsing(self):
        raw_string = "status: success Operation completed"
        event = SirilEvent(raw_string)

        assert event.value == SirilEvent.STATUS
        assert event.status == "success"
        assert event.message == "Operation completed"
        assert event.progress == 0
        assert str(event) == raw_string

    def test_status_event_with_error(self):
        raw_string = "status: error Something went wrong"
        event = SirilEvent(raw_string)

        assert event.value == SirilEvent.STATUS
        assert event.status == "error"
        assert event.message == "Something went wrong"
        assert event.errored is True
        assert event.completed is True

    def test_status_event_with_exit(self):
        raw_string = "status: exit Exiting application"
        event = SirilEvent(raw_string)

        assert event.value == SirilEvent.STATUS
        assert event.status == "exit"
        assert event.message == "Exiting application"
        assert event.completed is True

    def test_progress_event_parsing(self):
        raw_string = "progress: 75"
        event = SirilEvent(raw_string)

        assert event.value == SirilEvent.PROGRESS
        assert event.progress == 75
        assert event.status is None
        assert event.message is None

    def test_progress_event_zero(self):
        raw_string = "progress: 0"
        event = SirilEvent(raw_string)

        assert event.value == SirilEvent.PROGRESS
        assert event.progress == 0

    def test_progress_event_hundred(self):
        raw_string = "progress: 100"
        event = SirilEvent(raw_string)

        assert event.value == SirilEvent.PROGRESS
        assert event.progress == 100

    def test_log_event_parsing(self):
        raw_string = "log: This is a log message"
        event = SirilEvent(raw_string)

        assert event.value == SirilEvent.LOG
        assert event.message == "This is a log message"
        assert event.status is None
        assert event.progress == 0

    def test_ready_event_parsing(self):
        raw_string = "ready"
        event = SirilEvent(raw_string)

        assert event.value == SirilEvent.STATUS
        assert event.status == "ready"
        assert event.siril_ready is True
        assert event.completed is False

    def test_unrecognized_event_as_log(self):
        raw_string = "Some random output from siril"
        event = SirilEvent(raw_string)

        assert event.value == SirilEvent.LOG
        assert event.message == "Some random output from siril"
        assert event.status is None

    def test_empty_string_event(self):
        raw_string = ""
        event = SirilEvent(raw_string)

        assert event.value == SirilEvent.LOG
        assert event.message == ""
        assert event.status is None

    def test_status_event_without_message(self):
        raw_string = "status: running"
        event = SirilEvent(raw_string)

        assert event.value == SirilEvent.STATUS
        # Regex requires space + message, so this won't match
        assert event.status is None
        assert event.message is None

    def test_status_event_with_colon_in_message(self):
        raw_string = "status: success File saved: /path/to/file.fits"
        event = SirilEvent(raw_string)

        assert event.value == SirilEvent.STATUS
        assert event.status == "success"
        assert event.message == "File saved: /path/to/file.fits"

    def test_log_event_with_special_characters(self):
        raw_string = "log: Processing file with special chars: éñ§™"
        event = SirilEvent(raw_string)

        assert event.value == SirilEvent.LOG
        assert event.message == "Processing file with special chars: éñ§™"

    def test_progress_event_invalid_number(self):
        raw_string = "progress: abc"
        event = SirilEvent(raw_string)

        assert event.value == SirilEvent.PROGRESS
        assert event.progress is None

    def test_progress_event_empty_number(self):
        raw_string = "progress: "
        event = SirilEvent(raw_string)

        assert event.value == SirilEvent.PROGRESS
        assert event.progress is None

    def test_completed_property_success(self):
        event = SirilEvent("status: success All done")
        assert event.completed is True

    def test_completed_property_error(self):
        event = SirilEvent("status: error Failed")
        assert event.completed is True

    def test_completed_property_exit(self):
        event = SirilEvent("status: exit Goodbye")
        assert event.completed is True

    def test_completed_property_running(self):
        event = SirilEvent("status: running Still working")
        assert event.completed is False

    def test_errored_property_true(self):
        event = SirilEvent("status: error Something failed")
        assert event.errored is True

    def test_errored_property_false(self):
        event = SirilEvent("status: success All good")
        assert event.errored is False

    def test_siril_ready_property_true(self):
        event = SirilEvent("ready")
        assert event.siril_ready is True

    def test_siril_ready_property_false(self):
        event = SirilEvent("status: running Still working")
        assert event.siril_ready is False

    def test_str_representation(self):
        raw_string = "status: success Operation completed successfully"
        event = SirilEvent(raw_string)
        assert str(event) == raw_string

    def test_status_parsing_edge_cases(self):
        # Test status with no space after colon
        event = SirilEvent("status:success")
        assert event.status is None
        assert event.message is None

    def test_log_parsing_edge_cases(self):
        # Test log with no space after colon
        event = SirilEvent("log:message")
        assert event.message is None

    def test_progress_parsing_with_large_number(self):
        raw_string = "progress: 999999"
        event = SirilEvent(raw_string)

        assert event.value == SirilEvent.PROGRESS
        assert event.progress == 999999

    def test_status_event_with_multiple_spaces(self):
        raw_string = "status:   success    Multiple spaces in message"
        event = SirilEvent(raw_string)

        assert event.value == SirilEvent.STATUS
        # The regex \s(\S*)\s doesn't handle multiple spaces well
        assert event.status is None  # No match due to regex behavior
        assert event.message == " success    Multiple spaces in message"

    def test_constants_values(self):
        assert SirilEvent.LOG == "log"
        assert SirilEvent.PROGRESS == "progress"
        assert SirilEvent.STATUS == "status"
