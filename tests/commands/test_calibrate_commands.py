import async_siril.command as command


def test_calibrate_unit_flats():
    _command = command.calibrate("sequence", "master bias ISO1600.fits", cfa=True, prefix="calibrated_flat_")
    assert str(_command) == "calibrate sequence '-bias=master bias ISO1600.fits' -cfa -prefix=calibrated_flat_"
    assert _command.valid


def test_calibrate_color_basic():
    _command = command.calibrate(
        "seq", dark="master_dark", flat="calibrated_master_flat", cfa=True, debayer=True, equalize_cfa=True
    )
    assert str(_command) == "calibrate seq -dark=master_dark -flat=calibrated_master_flat -cfa -debayer -equalize_cfa"
    assert _command.valid


def test_calibrate_mono_darkopt():
    _command = command.calibrate(
        "light_",
        bias="=$OFFSET*64",
        dark="master_dark_30s",
        flat="pp_flat_stacked",
        dark_optimization=True,
        prefix="dopp_",
        cosmetic_correction_from_dark=False,
        cosmetic_correction_from_bad_pixel_map="bad pixels.txt",
    )
    assert (
        str(_command)
        == "calibrate light_ -bias==$OFFSET*64 -dark=master_dark_30s -flat=pp_flat_stacked -cc=bpm 'bad pixels.txt' -opt -prefix=dopp_"
    )
    assert _command.valid


def test_seqextract_Green():
    _command = command.seqextract_Green("theseq")
    assert str(_command) == "seqextract_Green theseq"
    assert _command.valid


def test_setfindstar_sigma():
    _command = command.setfindstar(sigma=4)
    assert str(_command) == "setfindstar -sigma=4"
    assert _command.valid


def test_setfindstar_many():
    _command = command.setfindstar(
        reset=True, sigma=3, focal=3960, pixsize=5.4, roundness=0.7, moffat=True, relax=False
    )
    assert str(_command) == "setfindstar reset -sigma=3 -roundness=0.7 -focal=3960 -pixelsize=5.4 -moffat -relax=off"
    assert _command.valid


def test_seqfind_cosme():
    _command = command.seqfind_cosme("the_seq", 2.4, 5.5)
    assert str(_command) == "seqfind_cosme the_seq 2.4 5.5"
    assert _command.valid


class TestCalibrateSingleCommand:
    def test_calibrate_single_basic(self):
        _command = command.calibrate_single("sequence", "master bias ISO1600.fits", cfa=True, prefix="calibrated_flat_")
        assert (
            str(_command) == "calibrate_single sequence '-bias=master bias ISO1600.fits' -cfa -prefix=calibrated_flat_"
        )
        assert _command.valid


class TestMergeCommand:
    def test_merge_basic(self):
        _command = command.merge("sequence1", "sequence2", "output_sequence")
        assert str(_command) == "merge sequence1 sequence2 output_sequence"
        assert _command.valid


class TestMergeCfaCommand:
    def test_merge_cfa_basic(self):
        _command = command.merge_cfa("file_CFA0", "file_CFA1", "file_CFA2", "file_CFA3", "RGB")
        assert str(_command) == "merge_cfa file_CFA0 file_CFA1 file_CFA2 file_CFA3 RGB"
        assert _command.valid


class TestStackallCommand:
    def test_stackall_basic(self):
        _command = command.stackall()
        assert str(_command) == "stackall rej w 3 3 -nonorm"
        assert _command.valid


class TestWreconsCommand:
    def test_wrecons_basic(self):
        _command = command.wrecons(1.2, 3, 6.7)
        assert str(_command) == "wrecons 1.2 3 6.7"
        assert _command.valid
