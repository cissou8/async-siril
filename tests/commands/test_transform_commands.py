from async_siril.command import (
    boxselect,
    crop,
    mirrorx,
    mirrorx_single,
    mirrory,
    rotate,
    rotatePi,
    select,
    seqcrop,
    merge_cfa,
)
from async_siril.command_types import Rect, pixel_interpolation


class TestBoxSelectCommand:
    def test_boxselect_basic(self):
        cmd = boxselect()
        assert str(cmd) == "boxselect"
        assert cmd.valid is True

    def test_boxselect_clear(self):
        cmd = boxselect(clear=True)
        assert str(cmd) == "boxselect -clear"
        assert cmd.valid is True

    def test_boxselect_rect(self):
        cmd = boxselect(rect=Rect(0, 0, 10, 10))
        assert str(cmd) == "boxselect '0 0 10 10'"
        assert cmd.valid is True

    def test_boxselect_clear_rect(self):
        cmd = boxselect(clear=True, rect=Rect(0, 0, 10, 10))
        assert str(cmd) == "boxselect -clear"
        assert cmd.valid is True


class TestCropCommand:
    def test_crop_basic(self):
        cmd = crop()
        assert str(cmd) == "crop"
        assert cmd.valid is True

    def test_crop_rect(self):
        cmd = crop(rect=Rect(0, 0, 10, 10))
        assert str(cmd) == "crop '0 0 10 10'"
        assert cmd.valid is True


class TestMirrorXCommand:
    def test_mirrorx_basic(self):
        cmd = mirrorx()
        assert str(cmd) == "mirrorx -bottomup"
        assert cmd.valid is True

    def test_mirrorx_bottom_up(self):
        cmd = mirrorx(bottom_up=False)
        assert str(cmd) == "mirrorx"
        assert cmd.valid is True


class TestMirrorXSingleCommand:
    def test_mirrorx_single_basic(self):
        cmd = mirrorx_single("filename")
        assert str(cmd) == "mirrorx_single filename"
        assert cmd.valid is True


class TestMirrorYCommand:
    def test_mirrory_basic(self):
        cmd = mirrory()
        assert str(cmd) == "mirrory"
        assert cmd.valid is True


class TestRotateCommand:
    def test_rotate_basic(self):
        cmd = rotate(1.2)
        assert str(cmd) == "rotate 1.2"
        assert cmd.valid is True

    def test_rotate_nocrop(self):
        cmd = rotate(1.2, nocrop=True)
        assert str(cmd) == "rotate 1.2 -nocrop"
        assert cmd.valid is True

    def test_rotate_interp(self):
        cmd = rotate(1.2, interp=pixel_interpolation.INTERP_LINEAR)
        assert str(cmd) == "rotate 1.2 -interp=linear"
        assert cmd.valid is True

    def test_rotate_noclamp(self):
        cmd = rotate(1.2, noclamp=True)
        assert str(cmd) == "rotate 1.2 -noclamp"
        assert cmd.valid is True


class TestRotatePiCommand:
    def test_rotate_pi_basic(self):
        cmd = rotatePi()
        assert str(cmd) == "rotatePi"
        assert cmd.valid is True


class TestSelectCommand:
    def test_select_basic(self):
        cmd = select("sequence", 0, 10)
        assert str(cmd) == "select sequence 0 10"
        assert cmd.valid is True


class TestSeqCropCommand:
    def test_seqcrop_basic(self):
        cmd = seqcrop("sequence", Rect(0, 0, 10, 10))
        assert str(cmd) == "seqcrop sequence '0 0 10 10'"
        assert cmd.valid is True

    def test_seqcrop_prefix(self):
        cmd = seqcrop("sequence", Rect(0, 0, 10, 10), prefix="prefix")
        assert str(cmd) == "seqcrop sequence '0 0 10 10' -prefix=prefix"
        assert cmd.valid is True


class TestMergeCFACommand:
    def test_merge_cfa_basic(self):
        cmd = merge_cfa("file_CFA0", "file_CFA1", "file_CFA2", "file_CFA3", "bayerpattern")
        assert str(cmd) == "merge_cfa file_CFA0 file_CFA1 file_CFA2 file_CFA3 bayerpattern"
        assert cmd.valid is True
