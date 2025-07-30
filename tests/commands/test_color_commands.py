import async_siril.command as command
import pytest


class TestPccCommand:
    def test_pcc_basic(self):
        _command = command.pcc()
        assert str(_command) == "pcc"
        assert _command.valid


class TestRgbcompCommand:
    def test_rgbcomp_validation(self):
        with pytest.raises(ValueError):
            command.rgbcomp()

    def test_rgbcomp_rgb(self):
        _command = command.rgbcomp(red_image="r", green_image="g", blue_image="b")
        assert str(_command) == "rgbcomp r g b"
        assert _command.valid

    def test_rgbcomp_luminance_without_rgb(self):
        with pytest.raises(ValueError):
            command.rgbcomp(luminance="L_stacked")

    def test_rgbcomp_rgb_luminance(self):
        _command = command.rgbcomp(luminance="L_stacked", rgb_image="rgb")
        assert str(_command) == "rgbcomp -lum=L_stacked rgb"
        assert _command.valid

    def test_rgbcomp_all(self):
        _command = command.rgbcomp(
            luminance="L_stacked", red_image="r", green_image="g", blue_image="b", out="supercompo"
        )
        assert str(_command) == "rgbcomp -lum=L_stacked r g b -out=supercompo"
        assert _command.valid


class TestRgradientCommand:
    def test_rgradient_basic(self):
        _command = command.rgradient(xc=0, yc=0, dR=0, dalpha=0)
        assert str(_command) == "rgradient 0 0 0 0"
        assert _command.valid


class TestRlCommand:
    def test_rl_basic(self):
        _command = command.rl()
        assert str(_command) == "rl"
        assert _command.valid


class TestSpccCommand:
    def test_spcc_basic(self):
        _command = command.spcc(oscsensor="oscsensor")
        assert str(_command) == "spcc -oscsensor=oscsensor -narrowband"
        assert _command.valid


class TestCcmCommand:
    def test_ccm_basic(self):
        _command = command.ccm(m00=0, m01=0, m02=0, m10=0, m11=0, m12=0, m20=0, m21=0, m22=0)
        assert str(_command) == "ccm 0 0 0 0 0 0 0 0 0"
        assert _command.valid

    def test_ccm_gamma(self):
        _command = command.ccm(m00=0, m01=0, m02=0, m10=0, m11=0, m12=0, m20=0, m21=0, m22=0, gamma=1.2)
        assert str(_command) == "ccm 0 0 0 0 0 0 0 0 0 1.2"
        assert _command.valid


class TestSeqCcmCommand:
    def test_seqccm_basic(self):
        _command = command.seqccm(sequencename="sequence")
        assert str(_command) == "seqccm sequence"
        assert _command.valid

    def test_seqccm_prefix(self):
        _command = command.seqccm(sequencename="sequence", prefix="prefix")
        assert str(_command) == "seqccm sequence -prefix=prefix"
        assert _command.valid


class TestSbCommand:
    def test_sb_basic(self):
        _command = command.sb()
        assert str(_command) == "sb"
        assert _command.valid


class TestSeqSbCommand:
    def test_seqsb_basic(self):
        _command = command.seqsb("sequence")
        assert str(_command) == "seqsb sequence"
        assert _command.valid


class TestIccAssignCommand:
    def test_icc_assign_basic(self):
        _command = command.icc_assign("profile")
        assert str(_command) == "icc_assign profile"
        assert _command.valid


class TestIccConvertToCommand:
    def test_icc_convert_to_basic(self):
        _command = command.icc_convert_to("profile")
        assert str(_command) == "icc_convert_to profile"
        assert _command.valid
