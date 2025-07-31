import async_siril.command as command


class TestAutostretchCommand:
    def test_autostretch(self):
        cmd = command.autostretch(linked=True, target_background=0.15, shadows_clipping=-10)
        assert str(cmd) == "autostretch -linked -10 0.15"
        assert cmd.valid

    def test_autostretch_default(self):
        cmd = command.autostretch()
        assert str(cmd) == "autostretch"
        assert cmd.valid


class TestAutoghsCommand:
    def test_autoghs_basic(self):
        cmd = command.autoghs(1, 2)
        assert str(cmd) == "autoghs 1 2"
        assert cmd.valid is True

    def test_autoghs_linked(self):
        cmd = command.autoghs(1, 2, linked=True)
        assert str(cmd) == "autoghs -linked 1 2"
        assert cmd.valid is True


class TestInvGhtCommand:
    def test_invght_basic(self):
        cmd = command.invght(1.2)
        assert str(cmd) == "invght -D=1.2"
        assert cmd.valid is True


class TestInvModAsinhCommand:
    def test_invmodasinh_basic(self):
        cmd = command.invmodasinh(1.2)
        assert str(cmd) == "invmodasinh -D=1.2"
        assert cmd.valid is True


class TestInvMtfCommand:
    def test_invmtf_basic(self):
        cmd = command.invmtf(1.2, 2.2, 3.5)
        assert str(cmd) == "invmtf 1.2 2.2 3.5"
        assert cmd.valid is True


class TestLinearMatchCommand:
    def test_linear_match_basic(self):
        cmd = command.linear_match("image", 1.2, 3.2)
        assert str(cmd) == "linear_match image 1.2 3.2"
        assert cmd.valid is True


class TestLinstretchCommand:
    def test_linstretch_basic(self):
        cmd = command.linstretch(1.2)
        assert str(cmd) == "linstretch -BP=1.2"
        assert cmd.valid is True


class TestModAsinhCommand:
    def test_modasinh_basic(self):
        cmd = command.modasinh(1.2)
        assert str(cmd) == "modasinh -D=1.2"
        assert cmd.valid is True


class TestMtfCommand:
    def test_mtf_basic(self):
        cmd = command.mtf(1.2, 2.2, 3.5)
        assert str(cmd) == "mtf 1.2 2.2 3.5"
        assert cmd.valid is True


class TestSeqLinstretchCommand:
    def test_seqlinstretch_basic(self):
        cmd = command.seqlinstretch("sequence", 1.2)
        assert str(cmd) == "seqlinstretch sequence -BP=1.2"
        assert cmd.valid is True


class TestSeqMtfCommand:
    def test_seqmtf_basic(self):
        cmd = command.seqmtf("sequence", 1.2, 2.2, 3.5)
        assert str(cmd) == "seqmtf sequence 1.2 2.2 3.5"
        assert cmd.valid is True


class TestAsinhCommand:
    def test_asinh(self):
        _command = command.asinh(100)
        assert str(_command) == "asinh 100"
        assert _command.valid

    def test_asinh_all(self):
        _command = command.asinh(100, True, 0.001)
        assert str(_command) == "asinh -human 100 0.001"
        assert _command.valid
