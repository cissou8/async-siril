from async_siril.command import (
    extract,
    extract_Green,
    extract_Ha,
    extract_HaOIII,
    seqextract_Green,
    seqextract_Ha,
    seqextract_HaOIII,
    unpurple,
    rmgreen,
)
from async_siril.command_types import extract_resample, rmgreen_protection


class TestExtractCommands:
    def test_extract_basic(self):
        cmd = extract(1)

        assert str(cmd) == "extract -nbplans=1"
        assert cmd.valid is True

    def test_extract_green(self):
        cmd = extract_Green()

        assert str(cmd) == "extract_Green"
        assert cmd.valid is True

    def test_extract_ha(self):
        cmd = extract_Ha()

        assert str(cmd) == "extract_Ha"
        assert cmd.valid is True

    def test_extract_ha_upscale(self):
        cmd = extract_Ha(upscale=True)

        assert str(cmd) == "extract_Ha -upscale"
        assert cmd.valid is True

    def test_extract_haoiii_basic(self):
        cmd = extract_HaOIII()

        assert str(cmd) == "extract_HaOIII"
        assert cmd.valid is True

    def test_extract_haoiii_resample(self):
        cmd = extract_HaOIII(resample=extract_resample.HA)

        assert str(cmd) == "extract_HaOIII -resample=ha"
        assert cmd.valid is True


class TestSequenceExtractCommands:
    def test_sequence_extract_green(self):
        cmd = seqextract_Green("sequence")

        assert str(cmd) == "seqextract_Green sequence"
        assert cmd.valid is True

    def test_sequence_extract_green_prefix(self):
        cmd = seqextract_Green("sequence", prefix="prefix")

        assert str(cmd) == "seqextract_Green sequence -prefix=prefix"
        assert cmd.valid is True

    def test_sequence_extract_ha_basic(self):
        cmd = seqextract_Ha("sequence")

        assert str(cmd) == "seqextract_Ha sequence"
        assert cmd.valid is True

    def test_sequence_extract_ha_prefix(self):
        cmd = seqextract_Ha("sequence", prefix="prefix")

        assert str(cmd) == "seqextract_Ha sequence -prefix=prefix"
        assert cmd.valid is True

    def test_sequence_extract_ha_upscale(self):
        cmd = seqextract_Ha("sequence", upscale=True)

        assert str(cmd) == "seqextract_Ha sequence -upscale"
        assert cmd.valid is True

    def test_sequence_extract_haoiii_basic(self):
        cmd = seqextract_HaOIII("sequence")

        assert str(cmd) == "seqextract_HaOIII sequence"
        assert cmd.valid is True

    def test_sequence_extract_haoiii_resample(self):
        cmd = seqextract_HaOIII("sequence", resample=extract_resample.HA)

        assert str(cmd) == "seqextract_HaOIII sequence -resample=ha"
        assert cmd.valid is True


class TestUnpurpleCommands:
    def test_unpurple_basic(self):
        cmd = unpurple()

        assert str(cmd) == "unpurple"
        assert cmd.valid is True

    def test_unpurple_starmask(self):
        cmd = unpurple(starmask=True)

        assert str(cmd) == "unpurple -starmask"
        assert cmd.valid is True

    def test_unpurple_blue_threshold(self):
        cmd = unpurple(blue=1.2, thresh=0.8)

        assert str(cmd) == "unpurple -blue=1.2 -thresh=0.8"
        assert cmd.valid is True


class TestRmGreenCommand:
    def test_rm_green_basic(self):
        cmd = rmgreen()

        assert str(cmd) == "rmgreen"
        assert cmd.valid is True

    def test_rm_green_protection(self):
        cmd = rmgreen(protection=rmgreen_protection.ADDITIVE_MASK, amount=1.2)

        assert str(cmd) == "rmgreen 3 1.2"
        assert cmd.valid is True
