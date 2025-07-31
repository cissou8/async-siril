import async_siril.command as command
import async_siril.command_types as ct


class TestExtractCommands:
    def test_extract_basic(self):
        cmd = command.extract(1)

        assert str(cmd) == "extract -nbplans=1"
        assert cmd.valid is True

    def test_extract_green(self):
        cmd = command.extract_Green()

        assert str(cmd) == "extract_Green"
        assert cmd.valid is True

    def test_extract_ha(self):
        cmd = command.extract_Ha()

        assert str(cmd) == "extract_Ha"
        assert cmd.valid is True

    def test_extract_ha_upscale(self):
        cmd = command.extract_Ha(upscale=True)

        assert str(cmd) == "extract_Ha -upscale"
        assert cmd.valid is True

    def test_extract_haoiii_basic(self):
        cmd = command.extract_HaOIII()

        assert str(cmd) == "extract_HaOIII"
        assert cmd.valid is True

    def test_extract_haoiii_resample(self):
        cmd = command.extract_HaOIII(resample=ct.extract_resample.HA)

        assert str(cmd) == "extract_HaOIII -resample=ha"
        assert cmd.valid is True


class TestSequenceExtractCommands:
    def test_sequence_extract_green(self):
        cmd = command.seqextract_Green("sequence")

        assert str(cmd) == "seqextract_Green sequence"
        assert cmd.valid is True

    def test_sequence_extract_green_prefix(self):
        cmd = command.seqextract_Green("sequence", prefix="prefix")

        assert str(cmd) == "seqextract_Green sequence -prefix=prefix"
        assert cmd.valid is True

    def test_sequence_extract_ha_basic(self):
        cmd = command.seqextract_Ha("sequence")

        assert str(cmd) == "seqextract_Ha sequence"
        assert cmd.valid is True

    def test_sequence_extract_ha_prefix(self):
        cmd = command.seqextract_Ha("sequence", prefix="prefix")

        assert str(cmd) == "seqextract_Ha sequence -prefix=prefix"
        assert cmd.valid is True

    def test_sequence_extract_ha_upscale(self):
        cmd = command.seqextract_Ha("sequence", upscale=True)

        assert str(cmd) == "seqextract_Ha sequence -upscale"
        assert cmd.valid is True

    def test_sequence_extract_haoiii_basic(self):
        cmd = command.seqextract_HaOIII("sequence")

        assert str(cmd) == "seqextract_HaOIII sequence"
        assert cmd.valid is True

    def test_sequence_extract_haoiii_resample(self):
        cmd = command.seqextract_HaOIII("sequence", resample=ct.extract_resample.HA)

        assert str(cmd) == "seqextract_HaOIII sequence -resample=ha"
        assert cmd.valid is True


class TestUnpurpleCommands:
    def test_unpurple_basic(self):
        cmd = command.unpurple()

        assert str(cmd) == "unpurple"
        assert cmd.valid is True

    def test_unpurple_starmask(self):
        cmd = command.unpurple(starmask=True)

        assert str(cmd) == "unpurple -starmask"
        assert cmd.valid is True

    def test_unpurple_blue_threshold(self):
        cmd = command.unpurple(blue=1.2, thresh=0.8)

        assert str(cmd) == "unpurple -blue=1.2 -thresh=0.8"
        assert cmd.valid is True


class TestRmGreenCommand:
    def test_rm_green_basic(self):
        cmd = command.rmgreen()

        assert str(cmd) == "rmgreen"
        assert cmd.valid is True

    def test_rm_green_protection(self):
        cmd = command.rmgreen(protection=ct.rmgreen_protection.ADDITIVE_MASK, amount=1.2)

        assert str(cmd) == "rmgreen 3 1.2"
        assert cmd.valid is True


class TestSeqExtractGreenCommand:
    def test_seqextract_Green(self):
        _command = command.seqextract_Green("theseq")
        assert str(_command) == "seqextract_Green theseq"
        assert _command.valid


class TestSubskyCommand:
    def test_subsky(self):
        _command = command.subsky(degree=2, samples=30)
        assert str(_command) == "subsky 2 -samples=30"
        assert _command.valid

    def test_seqsubsky(self):
        _command = command.seqsubsky(sequence="pp_light_", tolerance=0.5)
        assert str(_command) == "seqsubsky pp_light_ 1 -tolerance=0.5"
        assert _command.valid
