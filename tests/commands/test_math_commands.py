import pytest
import async_siril.command as command
import async_siril.command_types as ct


class TestFdivCommand:
    def test_fdiv_basic(self):
        cmd = command.fdiv("filename", 2)
        assert str(cmd) == "fdiv filename 2"
        assert cmd.valid is True


class TestFFillCommand:
    def test_ffill_basic(self):
        cmd = command.ffill(2)
        assert str(cmd) == "ffill 2"
        assert cmd.valid is True

    def test_ffill_with_rect(self):
        cmd = command.ffill(2, rect=ct.Rect(0, 0, 10, 10))
        # TODO: fix this, is it right?
        assert str(cmd) == "ffill 2 '0 0 10 10'"
        assert cmd.valid is True


class TestFMulCommand:
    def test_fmul_basic(self):
        cmd = command.fmul(2)
        assert str(cmd) == "fmul 2"
        assert cmd.valid is True


class TestFMedianCommand:
    def test_fmedian_basic(self):
        cmd = command.fmedian(1, 1.2)
        assert str(cmd) == "fmedian 1 1.2"
        assert cmd.valid is True

    def test_fmedian_invalid_ksize(self):
        with pytest.raises(ValueError):
            command.fmedian(2, 1.2)


class TestFillCommand:
    def test_fill_basic(self):
        cmd = command.fill(2)
        assert str(cmd) == "fill 2"
        assert cmd.valid is True

    def test_fill_with_rect(self):
        cmd = command.fill(2, rect=ct.Rect(0, 0, 10, 10))
        # TODO: fix this, is it right?
        assert str(cmd) == "fill 2 '0 0 10 10'"
        assert cmd.valid is True


class TestIdivCommand:
    def test_idiv_basic(self):
        cmd = command.idiv("filename")
        assert str(cmd) == "idiv filename"
        assert cmd.valid is True


class TestImulCommand:
    def test_imul_basic(self):
        cmd = command.imul("filename")
        assert str(cmd) == "imul filename"
        assert cmd.valid is True


class TestIsubCommand:
    def test_isub_basic(self):
        cmd = command.isub("filename")
        assert str(cmd) == "isub filename"
        assert cmd.valid is True


class TestIaddCommand:
    def test_iadd_basic(self):
        cmd = command.iadd("filename")
        assert str(cmd) == "iadd filename"
        assert cmd.valid is True


class TestPmCommand:
    def test_pm_basic(self):
        cmd = command.pm("$image1$ * 0.5 + $image2$ * 0.5")
        assert str(cmd) == "pm '$image1$ * 0.5 + $image2$ * 0.5'"
        assert cmd.valid is True

    def test_pm_rescale(self):
        cmd = command.pm("$image1$ * 0.5 + $image2$ * 0.5", rescale=True)
        assert str(cmd) == "pm '$image1$ * 0.5 + $image2$ * 0.5' -rescale"
        assert cmd.valid is True

    def test_pm_rescale_with_low_high(self):
        cmd = command.pm("$image1$ * 0.5 + $image2$ * 0.5", rescale=True, rescale_low=0.1, rescale_high=0.9)
        assert str(cmd) == "pm '$image1$ * 0.5 + $image2$ * 0.5' -rescale 0.1 0.9"
        assert cmd.valid is True

    def test_pm_rescale_with_low_nosum(self):
        cmd = command.pm("$image1$ * 0.5 + $image2$ * 0.5", rescale=True, rescale_low=0.1, rescale_high=0.9, nosum=True)
        assert str(cmd) == "pm '$image1$ * 0.5 + $image2$ * 0.5' -rescale 0.1 0.9 -nosum"
        assert cmd.valid is True


class TestOffsetCommand:
    def test_offset_basic(self):
        cmd = command.offset(2.1)
        assert str(cmd) == "offset 2.1"
        assert cmd.valid is True


class TestNozeroCommand:
    def test_nozero_basic(self):
        cmd = command.nozero(2)
        assert str(cmd) == "nozero 2"
        assert cmd.valid is True


class TestLimitCommand:
    def test_limit_basic(self):
        cmd = command.limit(ct.limit_option.CLIP)
        assert str(cmd) == "limit -clip"
        assert cmd.valid is True
