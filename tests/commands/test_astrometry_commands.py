import async_siril.command as command
import async_siril.command_types as ct


class TestCatSearchCommand:
    def test_catsearch_basic(self):
        cmd = command.catsearch("M31")
        assert str(cmd) == "catsearch M31"
        assert cmd.valid is True


class TestConesearchCommand:
    def test_conesearch_basic(self):
        cmd = command.conesearch()
        assert str(cmd) == "conesearch"
        assert cmd.valid is True


class TestFindCompStarsCommand:
    def test_findcompstars_basic(self):
        cmd = command.findcompstars("polaris")
        assert str(cmd) == "findcompstars polaris -dvmag=3 -dbv=0.5 -emag=0.03"
        assert cmd.valid is True


class TestSpccListCommand:
    def test_spcc_list_basic(self):
        cmd = command.spcc_list(ct.spcc_list_type.BLUEFILTER)
        assert str(cmd) == "spcc_list bluefilter"
        assert cmd.valid is True


class TestMakePSFCommand:
    def test_makepsf_basic(self):
        cmd = command.makepsf(ct.psf_method.STARS)
        assert str(cmd) == "makepsf stars"
        assert cmd.valid is True


class TestStarNetCommand:
    def test_starnet_basic(self):
        cmd = command.starnet()
        assert str(cmd) == "starnet"
        assert cmd.valid is True


class TestSeqStarNetCommand:
    def test_seqstarnet_basic(self):
        cmd = command.seqstarnet("sequence")
        assert str(cmd) == "seqstarnet sequence"
        assert cmd.valid is True


class TestSetPhotCommand:
    def test_setphot_basic(self):
        cmd = command.setphot()
        assert str(cmd) == "setphot"
        assert cmd.valid is True
