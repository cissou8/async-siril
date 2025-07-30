from async_siril.command import trixel, thresh, threshhi, threshlo, stat, seqstat, histo, bg, bgnoise, binxy
from async_siril.command_types import Channel, stat_detail


class TestBgCommand:
    def test_bg_basic(self):
        cmd = bg()
        assert str(cmd) == "bg"
        assert cmd.valid is True


class TestBgNoiseCommand:
    def test_bgnoise_basic(self):
        cmd = bgnoise()
        assert str(cmd) == "bgnoise"
        assert cmd.valid is True


class TestBinxyCommand:
    def test_binxy_basic(self):
        cmd = binxy(1.2)
        assert str(cmd) == "binxy 1.2"
        assert cmd.valid is True

    def test_binxy_sum(self):
        cmd = binxy(1.2, sum=True)
        assert str(cmd) == "binxy 1.2 -sum"
        assert cmd.valid is True


class TestHistoCommand:
    def test_histo_basic(self):
        cmd = histo(Channel.RED)
        assert str(cmd) == "histo 0"
        assert cmd.valid is True


class TestSeqStatCommand:
    def test_seqstat_basic(self):
        cmd = seqstat("sequence", "output_file")
        assert str(cmd) == "seqstat sequence output_file"
        assert cmd.valid is True

    def test_seqstat_option(self):
        cmd = seqstat("sequence", "output_file", option=stat_detail.BASIC)
        assert str(cmd) == "seqstat sequence output_file basic"
        assert cmd.valid is True

    def test_seqstat_cfa(self):
        cmd = seqstat("sequence", "output_file", cfa=True)
        assert str(cmd) == "seqstat sequence output_file -cfa"
        assert cmd.valid is True


class TestStatCommand:
    def test_stat_basic(self):
        cmd = stat()
        assert str(cmd) == "stat"
        assert cmd.valid is True

    def test_stat_cfa(self):
        cmd = stat(cfa=True)
        assert str(cmd) == "stat -cfa"
        assert cmd.valid is True

    def test_stat_cfa_main(self):
        cmd = stat(cfa=True, main="main")
        assert str(cmd) == "stat -cfa main"
        assert cmd.valid is True


class TestThreshCommand:
    def test_thresh_basic(self):
        cmd = thresh(1.2, 3.2)
        assert str(cmd) == "thresh 1.2 3.2"
        assert cmd.valid is True


class TestThreshHiCommand:
    def test_threshhi_basic(self):
        cmd = threshhi(3.2)
        assert str(cmd) == "threshhi 3.2"
        assert cmd.valid is True


class TestThreshLoCommand:
    def test_threshlo_basic(self):
        cmd = threshlo(1.2)
        assert str(cmd) == "threshlo 1.2"
        assert cmd.valid is True


class TestTrixelCommand:
    def test_trixel_basic(self):
        cmd = trixel()
        assert str(cmd) == "trixel"
        assert cmd.valid is True

    def test_trixel_print(self):
        cmd = trixel(p=True)
        assert str(cmd) == "trixel -p"
        assert cmd.valid is True
