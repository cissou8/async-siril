import async_siril.command as command
import async_siril.command_types as ct


class TestClaheCommand:
    def test_clahe_basic(self):
        cmd = command.clahe(1.2, 3.4)
        assert str(cmd) == "clahe 1.2 3.4"
        assert cmd.valid


class TestGaussCommand:
    def test_gauss_basic(self):
        cmd = command.gauss(1.2)
        assert str(cmd) == "gauss 1.2"
        assert cmd.valid


class TestGhtCommand:
    def test_ght_basic(self):
        cmd = command.ght(1.2)
        assert str(cmd) == "ght -D=1.2"
        assert cmd.valid


class TestSeqGhtCommand:
    def test_seqght_basic(self):
        cmd = command.seqght("sequence", 1.2)
        assert str(cmd) == "seqght sequence -D=1.2"
        assert cmd.valid

    def test_seqght_prefix(self):
        cmd = command.seqght("sequence", 1.2, prefix="prefix")
        assert str(cmd) == "seqght sequence -D=1.2 -prefix=prefix"
        assert cmd.valid


class TestSeqInvGhtCommand:
    def test_seqinvght_basic(self):
        cmd = command.seqinvght("sequence", 1.2)
        assert str(cmd) == "seqinvght sequence -D=1.2"
        assert cmd.valid

    def test_seqinvght_prefix(self):
        cmd = command.seqinvght("sequence", 1.2, prefix="prefix")
        assert str(cmd) == "seqinvght sequence -D=1.2 -prefix=prefix"
        assert cmd.valid


class TestUnsharpCommand:
    def test_unsharp_basic(self):
        cmd = command.unsharp(1.2, 3.4)
        assert str(cmd) == "unsharp 1.2 3.4"
        assert cmd.valid


class TestWaveletCommand:
    def test_wavelet_basic(self):
        cmd = command.wavelet(2, ct.wavelet_type.BSPLINE)
        assert str(cmd) == "wavelet 2 2"
        assert cmd.valid


class TestWienerCommand:
    def test_wiener_basic(self):
        cmd = command.wiener()
        assert str(cmd) == "wiener"
        assert cmd.valid


class TestSeqWienerCommand:
    def test_seqwiener_basic(self):
        cmd = command.seqwiener("sequence")
        assert str(cmd) == "seqwiener sequence"
        assert cmd.valid


class TestDenoiseCommand:
    def test_denoise_basic(self):
        cmd = command.denoise()
        assert str(cmd) == "denoise"
        assert cmd.valid


class TestEpfCommand:
    def test_epf_basic(self):
        cmd = command.epf()
        assert str(cmd) == "epf"
        assert cmd.valid


class TestFixbandingCommand:
    def test_fixbanding_basic(self):
        cmd = command.fixbanding(1.2, 3.2)
        assert str(cmd) == "fixbanding 1.2 3.2"
        assert cmd.valid


class TestSeqFixbandingCommand:
    def test_seqfixbanding_basic(self):
        cmd = command.seqfixbanding("sequence", 1.2, 3.2)
        assert str(cmd) == "seqfixbanding sequence 1.2 3.2"
        assert cmd.valid

    def test_seqfixbanding_prefix(self):
        cmd = command.seqfixbanding("sequence", 1.2, 3.2, prefix="prefix")
        assert str(cmd) == "seqfixbanding sequence 1.2 3.2 -prefix=prefix"
        assert cmd.valid
