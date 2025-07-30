import async_siril.command as command


class TestStartLiveStackCommand:
    def test_start_live_stack_basic(self):
        cmd = command.start_ls()

        assert str(cmd) == "start_ls"
        assert cmd.valid is True

    def test_start_live_stack_with_dark(self):
        cmd = command.start_ls(dark="dark.fit")

        assert str(cmd) == "start_ls -dark=dark.fit"
        assert cmd.valid is True

    def test_start_live_stack_with_dark_and_flat(self):
        cmd = command.start_ls(dark="dark.fit", flat="flat.fit")

        assert str(cmd) == "start_ls -dark=dark.fit -flat=flat.fit"
        assert cmd.valid is True

    def test_start_live_stack_with_dark_and_flat_and_rotate(self):
        cmd = command.start_ls(dark="dark.fit", flat="flat.fit", rotate=True)

        assert str(cmd) == "start_ls -dark=dark.fit -flat=flat.fit -rotate"
        assert cmd.valid is True

    def test_start_live_stack_with_dark_and_flat_and_rotate_and_32bits(self):
        cmd = command.start_ls(dark="dark.fit", flat="flat.fit", rotate=True, bits_32=True)

        assert str(cmd) == "start_ls -dark=dark.fit -flat=flat.fit -rotate -32bits"
        assert cmd.valid is True


class TestStopLiveStackCommand:
    def test_stop_live_stack_basic(self):
        cmd = command.stop_ls()

        assert str(cmd) == "stop_ls"
        assert cmd.valid is True


class TestLiveStackCommand:
    def test_live_stack_basic(self):
        cmd = command.livestack("file.fit")

        assert str(cmd) == "livestack file.fit"
        assert cmd.valid is True
