import async_siril.command as command


class TestCosmeCommand:
    def test_cosme_basic(self):
        cmd = command.cosme("filename")
        assert str(cmd) == "cosme filename"
        assert cmd.valid


class TestSeqCosmeCommand:
    def test_seqcosme_basic(self):
        cmd = command.seqcosme("sequence", filename="filename")
        assert str(cmd) == "seqcosme sequence filename"
        assert cmd.valid

    def test_seqcosme_prefix(self):
        cmd = command.seqcosme("sequence", filename="filename", prefix="prefix")
        assert str(cmd) == "seqcosme sequence filename -prefix=prefix"
        assert cmd.valid


class TestCosmeCfaCommand:
    def test_cosme_cfa_basic(self):
        cmd = command.cosme_cfa("filename")
        assert str(cmd) == "cosme_cfa filename"
        assert cmd.valid


class TestSeqCosmeCfaCommand:
    def test_seqcosme_cfa_basic(self):
        cmd = command.seqcosme_cfa("sequence", filename="filename")
        assert str(cmd) == "seqcosme_cfa sequence filename"
        assert cmd.valid

    def test_seqcosme_cfa_prefix(self):
        cmd = command.seqcosme_cfa("sequence", filename="filename", prefix="prefix")
        assert str(cmd) == "seqcosme_cfa sequence filename -prefix=prefix"
        assert cmd.valid


class TestFindCosmeCommand:
    def test_find_cosme_basic(self):
        cmd = command.find_cosme(1.2, 3.4)
        assert str(cmd) == "find_cosme 1.2 3.4"
        assert cmd.valid


class TestSeqFindCosmeCommand:
    def test_seqfind_cosme_basic(self):
        cmd = command.seqfind_cosme("sequence", 1.2, 3.4)
        assert str(cmd) == "seqfind_cosme sequence 1.2 3.4"
        assert cmd.valid

    def test_seqfind_cosme_prefix(self):
        cmd = command.seqfind_cosme("sequence", 1.2, 3.4, prefix="prefix")
        assert str(cmd) == "seqfind_cosme sequence 1.2 3.4 -prefix=prefix"
        assert cmd.valid


class TestFindCosmeCfaCommand:
    def test_find_cosme_cfa_basic(self):
        cmd = command.find_cosme_cfa(1.2, 3.4)
        assert str(cmd) == "find_cosme_cfa 1.2 3.4"
        assert cmd.valid


class TestSeqFindCosmeCfaCommand:
    def test_seqfind_cosme_cfa_basic(self):
        cmd = command.seqfind_cosme_cfa("sequence", 1.2, 3.4)
        assert str(cmd) == "seqfind_cosme_cfa sequence 1.2 3.4"
        assert cmd.valid


class TestSeqFindCosmeCfaPrefixCommand:
    def test_seqfind_cosme_cfa_prefix(self):
        cmd = command.seqfind_cosme_cfa("sequence", 1.2, 3.4, prefix="prefix")
        assert str(cmd) == "seqfind_cosme_cfa sequence 1.2 3.4 -prefix=prefix"
        assert cmd.valid


class TestFindHotCommand:
    def test_find_hot_basic(self):
        cmd = command.find_hot("filename", 1.2, 3.4)
        assert str(cmd) == "find_hot filename 1.2 3.4"
        assert cmd.valid
