from async_siril.command import (
    extract,
    extract_Green,
    extract_Ha,
    extract_HaOIII,
    seqextract_Green,
    seqextract_Ha,
    seqextract_HaOIII,
)
from async_siril.command_types import extract_resample


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
