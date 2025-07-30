import pytest
from async_siril.command import fdiv, ffill, fmul, fmedian, fill, idiv, imul, isub, iadd, pm, offset, nozero, limit
from async_siril.command_types import Rect, limit_option


class TestFdivCommand:
    def test_fdiv_basic(self):
        cmd = fdiv("filename", 2)
        assert str(cmd) == "fdiv filename 2"
        assert cmd.valid is True


class TestFFillCommand:
    def test_ffill_basic(self):
        cmd = ffill(2)
        assert str(cmd) == "ffill 2"
        assert cmd.valid is True

    def test_ffill_with_rect(self):
        cmd = ffill(2, rect=Rect(0, 0, 10, 10))
        # TODO: fix this, is it right?
        assert str(cmd) == "ffill 2 '0 0 10 10'"
        assert cmd.valid is True


class TestFMulCommand:
    def test_fmul_basic(self):
        cmd = fmul(2)
        assert str(cmd) == "fmul 2"
        assert cmd.valid is True


class TestFMedianCommand:
    def test_fmedian_basic(self):
        cmd = fmedian(1, 1.2)
        assert str(cmd) == "fmedian 1 1.2"
        assert cmd.valid is True

    def test_fmedian_invalid_ksize(self):
        with pytest.raises(ValueError):
            fmedian(2, 1.2)


class TestFillCommand:
    def test_fill_basic(self):
        cmd = fill(2)
        assert str(cmd) == "fill 2"
        assert cmd.valid is True

    def test_fill_with_rect(self):
        cmd = fill(2, rect=Rect(0, 0, 10, 10))
        # TODO: fix this, is it right?
        assert str(cmd) == "fill 2 '0 0 10 10'"
        assert cmd.valid is True


class TestIdivCommand:
    def test_idiv_basic(self):
        cmd = idiv("filename")
        assert str(cmd) == "idiv filename"
        assert cmd.valid is True


class TestImulCommand:
    def test_imul_basic(self):
        cmd = imul("filename")
        assert str(cmd) == "imul filename"
        assert cmd.valid is True


class TestIsubCommand:
    def test_isub_basic(self):
        cmd = isub("filename")
        assert str(cmd) == "isub filename"
        assert cmd.valid is True


class TestIaddCommand:
    def test_iadd_basic(self):
        cmd = iadd("filename")
        assert str(cmd) == "iadd filename"
        assert cmd.valid is True


class TestPmCommand:
    def test_pm_basic(self):
        cmd = pm("$image1$ * 0.5 + $image2$ * 0.5")
        assert str(cmd) == "pm '$image1$ * 0.5 + $image2$ * 0.5'"
        assert cmd.valid is True

    def test_pm_rescale(self):
        cmd = pm("$image1$ * 0.5 + $image2$ * 0.5", rescale=True)
        assert str(cmd) == "pm '$image1$ * 0.5 + $image2$ * 0.5' -rescale"
        assert cmd.valid is True

    def test_pm_rescale_with_low_high(self):
        cmd = pm("$image1$ * 0.5 + $image2$ * 0.5", rescale=True, rescale_low=0.1, rescale_high=0.9)
        assert str(cmd) == "pm '$image1$ * 0.5 + $image2$ * 0.5' -rescale 0.1 0.9"
        assert cmd.valid is True

    def test_pm_rescale_with_low_nosum(self):
        cmd = pm("$image1$ * 0.5 + $image2$ * 0.5", rescale=True, rescale_low=0.1, rescale_high=0.9, nosum=True)
        assert str(cmd) == "pm '$image1$ * 0.5 + $image2$ * 0.5' -rescale 0.1 0.9 -nosum"
        assert cmd.valid is True


class TestOffsetCommand:
    def test_offset_basic(self):
        cmd = offset(2.1)
        assert str(cmd) == "offset 2.1"
        assert cmd.valid is True


class TestNozeroCommand:
    def test_nozero_basic(self):
        cmd = nozero(2)
        assert str(cmd) == "nozero 2"
        assert cmd.valid is True


class TestLimitCommand:
    def test_limit_basic(self):
        cmd = limit(limit_option.CLIP)
        assert str(cmd) == "limit -clip"
        assert cmd.valid is True
