import async_siril.command as command
import async_siril.command_types as ct
import pytest


class TestBoxSelectCommand:
    def test_boxselect_basic(self):
        cmd = command.boxselect()
        assert str(cmd) == "boxselect"
        assert cmd.valid is True

    def test_boxselect_clear(self):
        cmd = command.boxselect(clear=True)
        assert str(cmd) == "boxselect -clear"
        assert cmd.valid is True

    def test_boxselect_rect(self):
        cmd = command.boxselect(rect=ct.Rect(0, 0, 10, 10))
        assert str(cmd) == "boxselect '0 0 10 10'"
        assert cmd.valid is True

    def test_boxselect_clear_rect(self):
        cmd = command.boxselect(clear=True, rect=ct.Rect(0, 0, 10, 10))
        assert str(cmd) == "boxselect -clear"
        assert cmd.valid is True


class TestCropCommand:
    def test_crop_basic(self):
        cmd = command.crop()
        assert str(cmd) == "crop"
        assert cmd.valid is True

    def test_crop_rect(self):
        cmd = command.crop(rect=ct.Rect(0, 0, 10, 10))
        assert str(cmd) == "crop '0 0 10 10'"
        assert cmd.valid is True


class TestMirrorXCommand:
    def test_mirrorx_basic(self):
        cmd = command.mirrorx()
        assert str(cmd) == "mirrorx -bottomup"
        assert cmd.valid is True

    def test_mirrorx_bottom_up(self):
        cmd = command.mirrorx(bottom_up=False)
        assert str(cmd) == "mirrorx"
        assert cmd.valid is True


class TestMirrorXSingleCommand:
    def test_mirrorx_single_basic(self):
        cmd = command.mirrorx_single("filename")
        assert str(cmd) == "mirrorx_single filename"
        assert cmd.valid is True


class TestMirrorYCommand:
    def test_mirrory_basic(self):
        cmd = command.mirrory()
        assert str(cmd) == "mirrory"
        assert cmd.valid is True


class TestRotateCommand:
    def test_rotate_basic(self):
        cmd = command.rotate(1.2)
        assert str(cmd) == "rotate 1.2"
        assert cmd.valid is True

    def test_rotate_nocrop(self):
        cmd = command.rotate(1.2, nocrop=True)
        assert str(cmd) == "rotate 1.2 -nocrop"
        assert cmd.valid is True

    def test_rotate_interp(self):
        cmd = command.rotate(1.2, interp=ct.pixel_interpolation.INTERP_LINEAR)
        assert str(cmd) == "rotate 1.2 -interp=linear"
        assert cmd.valid is True

    def test_rotate_noclamp(self):
        cmd = command.rotate(1.2, noclamp=True)
        assert str(cmd) == "rotate 1.2 -noclamp"
        assert cmd.valid is True


class TestRotatePiCommand:
    def test_rotate_pi_basic(self):
        cmd = command.rotatePi()
        assert str(cmd) == "rotatePi"
        assert cmd.valid is True


class TestSelectCommand:
    def test_select_basic(self):
        cmd = command.select("sequence", 0, 10)
        assert str(cmd) == "select sequence 0 10"
        assert cmd.valid is True


class TestSeqCropCommand:
    def test_seqcrop_basic(self):
        cmd = command.seqcrop("sequence", ct.Rect(0, 0, 10, 10))
        assert str(cmd) == "seqcrop sequence '0 0 10 10'"
        assert cmd.valid is True

    def test_seqcrop_prefix(self):
        cmd = command.seqcrop("sequence", ct.Rect(0, 0, 10, 10), prefix="prefix")
        assert str(cmd) == "seqcrop sequence '0 0 10 10' -prefix=prefix"
        assert cmd.valid is True


class TestMergeCFACommand:
    def test_merge_cfa_basic(self):
        cmd = command.merge_cfa("file_CFA0", "file_CFA1", "file_CFA2", "file_CFA3", "bayerpattern")
        assert str(cmd) == "merge_cfa file_CFA0 file_CFA1 file_CFA2 file_CFA3 bayerpattern"
        assert cmd.valid is True


class TestFFTDCommand:
    def test_fftd_basic(self):
        cmd = command.fftd("1", "2")
        assert str(cmd) == "fftd 1 2"
        assert cmd.valid is True


class TestFFTICommand:
    def test_ffti_basic(self):
        cmd = command.ffti("1", "2")
        assert str(cmd) == "ffti 1 2"
        assert cmd.valid is True


class TestSplitCommand:
    def test_split(self):
        _command = command.split("r", "g", "b")
        assert str(_command) == "split r g b"
        assert _command.valid


class TestResampleCommand:
    def test_resample_ratio(self):
        _command = command.resample(factor=0.4)
        assert str(_command) == "resample 0.4"
        assert _command.valid

    def test_resample_target(self):
        _command = command.resample(target_height=400, interp=ct.pixel_interpolation.INTERP_AREA)
        assert str(_command) == "resample -height=400 -interp=area"
        assert _command.valid

    def test_resample_2targets(self):
        with pytest.raises(ValueError):
            command.resample(target_height=800, target_width=600)
