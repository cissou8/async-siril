import async_siril.command as command
import async_siril.command_types as ct


class TestBgCommand:
    def test_bg_basic(self):
        cmd = command.bg()
        assert str(cmd) == "bg"
        assert cmd.valid is True


class TestBgNoiseCommand:
    def test_bgnoise_basic(self):
        cmd = command.bgnoise()
        assert str(cmd) == "bgnoise"
        assert cmd.valid is True


class TestBinxyCommand:
    def test_binxy_basic(self):
        cmd = command.binxy(1.2)
        assert str(cmd) == "binxy 1.2"
        assert cmd.valid is True

    def test_binxy_sum(self):
        cmd = command.binxy(1.2, sum=True)
        assert str(cmd) == "binxy 1.2 -sum"
        assert cmd.valid is True


class TestHistoCommand:
    def test_histo_basic(self):
        cmd = command.histo(ct.Channel.RED)
        assert str(cmd) == "histo 0"
        assert cmd.valid is True


class TestSeqStatCommand:
    def test_seqstat_basic(self):
        cmd = command.seqstat("sequence", "output_file")
        assert str(cmd) == "seqstat sequence output_file"
        assert cmd.valid is True

    def test_seqstat_option(self):
        cmd = command.seqstat("sequence", "output_file", option=ct.stat_detail.BASIC)
        assert str(cmd) == "seqstat sequence output_file basic"
        assert cmd.valid is True

    def test_seqstat_cfa(self):
        cmd = command.seqstat("sequence", "output_file", cfa=True)
        assert str(cmd) == "seqstat sequence output_file -cfa"
        assert cmd.valid is True


class TestStatCommand:
    def test_stat_basic(self):
        cmd = command.stat()
        assert str(cmd) == "stat"
        assert cmd.valid is True

    def test_stat_cfa(self):
        cmd = command.stat(cfa=True)
        assert str(cmd) == "stat -cfa"
        assert cmd.valid is True

    def test_stat_cfa_main(self):
        cmd = command.stat(cfa=True, main="main")
        assert str(cmd) == "stat -cfa main"
        assert cmd.valid is True


class TestThreshCommand:
    def test_thresh_basic(self):
        cmd = command.thresh(1.2, 3.2)
        assert str(cmd) == "thresh 1.2 3.2"
        assert cmd.valid is True


class TestThreshHiCommand:
    def test_threshhi_basic(self):
        cmd = command.threshhi(3.2)
        assert str(cmd) == "threshhi 3.2"
        assert cmd.valid is True


class TestThreshLoCommand:
    def test_threshlo_basic(self):
        cmd = command.threshlo(1.2)
        assert str(cmd) == "threshlo 1.2"
        assert cmd.valid is True


class TestTrixelCommand:
    def test_trixel_basic(self):
        cmd = command.trixel()
        assert str(cmd) == "trixel"
        assert cmd.valid is True

    def test_trixel_print(self):
        cmd = command.trixel(p=True)
        assert str(cmd) == "trixel -p"
        assert cmd.valid is True


class TestLightCurveCommand:
    def test_light_curve_basic(self):
        cmd = command.light_curve("sequence", "output_file")
        assert str(cmd) == "light_curve sequence output_file"
        assert cmd.valid is True

    def test_light_curve(self):
        _command = command.light_curve("the_sequence", "0", ninastars="TYC 2688-1839-1.csv")
        assert str(_command) == "light_curve the_sequence 0 '-ninastars=TYC 2688-1839-1.csv'"
        assert _command.valid

    def test_light_curve_auto(self):
        _command = command.light_curve("the_sequence", "0", autoring=True, ninastars="TYC 2688-1839-1.csv")
        assert str(_command) == "light_curve the_sequence 0 -autoring '-ninastars=TYC 2688-1839-1.csv'"
        assert _command.valid


class TestProfileCommand:
    def test_profile_basic(self):
        cmd = command.profile((1, 2), (3, 4))
        assert str(cmd) == "profile -from=1,2 -to=3,4"
        assert cmd.valid is True


class TestPsfCommand:
    def test_psf_basic(self):
        cmd = command.psf("R")
        assert str(cmd) == "psf R"
        assert cmd.valid is True


class TestSeqProfileCommand:
    def test_seqprofile_basic(self):
        cmd = command.seqprofile("sequence", (1, 2), (3, 4))
        assert str(cmd) == "seqprofile sequence -from=1,2 -to=3,4"
        assert cmd.valid is True


class TestSeqPsfCommand:
    def test_seqpsf_basic(self):
        cmd = command.seqpsf("sequence", "R")
        assert str(cmd) == "seqpsf sequence R"
        assert cmd.valid is True
