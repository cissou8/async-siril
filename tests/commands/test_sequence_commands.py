import async_siril.command as command

#  Sequence-Only Operations:
#   - seqclean
#   - seqmerge_cfa
#   - seqmodasinh + seqinvmodasinh
#   - seqpsf
#   - seqresample
#   - seqrl
#   - seqsplit_cfa
#   - seqtilt


class TestSeqCleanCommand:
    def test_seqclean_basic(self):
        cmd = command.seqclean("sequence")
        assert str(cmd) == "seqclean sequence"
        assert cmd.valid

    def test_seqclean_all(self):
        cmd = command.seqclean("sequence", registration=True, statistics=True, selection=True)
        assert str(cmd) == "seqclean sequence -reg -stat -sel"
        assert cmd.valid


class TestSeqMergeCFACommand:
    def test_seqmerge_cfa_basic(self):
        cmd = command.seqmerge_cfa("sequence0", "sequence1", "sequence2", "sequence3", "RGB")
        assert str(cmd) == "seqmerge_cfa sequence0 sequence1 sequence2 sequence3 RGB"
        assert cmd.valid

    def test_seqmerge_cfa_prefix(self):
        cmd = command.seqmerge_cfa("sequence0", "sequence1", "sequence2", "sequence3", "RGB", prefixout="prefix")
        assert str(cmd) == "seqmerge_cfa sequence0 sequence1 sequence2 sequence3 RGB -prefixout=prefix"
        assert cmd.valid


class TestSeqModAsinhCommand:
    def test_seqmodasinh_basic(self):
        cmd = command.seqmodasinh("sequence", 1.2)
        assert str(cmd) == "seqmodasinh sequence -D=1.2"
        assert cmd.valid

    def test_seqmodasinh_prefix(self):
        cmd = command.seqmodasinh("sequence", 1.2, prefix="prefix")
        assert str(cmd) == "seqmodasinh sequence -D=1.2 -prefix=prefix"
        assert cmd.valid


class TestSeqInvModAsinhCommand:
    def test_seqinvmodasinh_basic(self):
        cmd = command.seqinvmodasinh("sequence", 1.2)
        assert str(cmd) == "seqinvmodasinh sequence -D=1.2"
        assert cmd.valid

    def test_seqinvmodasinh_prefix(self):
        cmd = command.seqinvmodasinh("sequence", 1.2, prefix="prefix")
        assert str(cmd) == "seqinvmodasinh sequence -D=1.2 -prefix=prefix"
        assert cmd.valid


class TestSeqPSFCommand:
    def test_seqpsf_basic(self):
        cmd = command.seqpsf("sequence", "R")
        assert str(cmd) == "seqpsf sequence R"
        assert cmd.valid


class TestSeqResampleCommand:
    def test_seqresample_basic(self):
        cmd = command.seqresample("sequence")
        assert str(cmd) == "seqresample sequence"
        assert cmd.valid

    def test_seqresample_prefix(self):
        cmd = command.seqresample("sequence", prefix="prefix")
        assert str(cmd) == "seqresample sequence -prefix=prefix"
        assert cmd.valid


class TestSeqRLCommand:
    def test_seqrl_basic(self):
        cmd = command.seqrl("sequence")
        assert str(cmd) == "seqrl sequence"
        assert cmd.valid


class TestSeqSplitCFACommand:
    def test_seqsplit_cfa_basic(self):
        cmd = command.seqsplit_cfa("sequence")
        assert str(cmd) == "seqsplit_cfa sequence"
        assert cmd.valid

    def test_seqsplit_cfa_prefix(self):
        cmd = command.seqsplit_cfa("sequence", prefix="prefix")
        assert str(cmd) == "seqsplit_cfa sequence -prefix=prefix"
        assert cmd.valid


class TestSeqTiltCommand:
    def test_seqtilt_basic(self):
        cmd = command.seqtilt("sequence")
        assert str(cmd) == "seqtilt sequence"
        assert cmd.valid
