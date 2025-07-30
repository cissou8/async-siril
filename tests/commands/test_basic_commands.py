import async_siril.command as command
import async_siril.command_types as ct


class TestSetCommands:
    def test_set_basic_string(self):
        cmd = command.set(key=ct.SirilSetting.MEM_MODE, value="1")

        assert str(cmd) == "set core.mem_mode=1"
        assert cmd.valid is True

    def test_set_basic_boolean(self):
        cmd = command.set(key=ct.SirilSetting.FORCE_16BIT, value=True)

        assert str(cmd) == "set core.force_16bit=True"
        assert cmd.valid is True

    def test_set_basic_number(self):
        cmd = command.set(key=ct.SirilSetting.MEM_RATIO, value=0.9)

        assert str(cmd) == "set core.mem_ratio=0.9"
        assert cmd.valid is True

    def test_setcpu_basic(self):
        cmd = command.setcpu(8)

        assert str(cmd) == "setcpu 8"
        assert cmd.valid is True

    def test_setmem_basic(self):
        cmd = command.setmem(ratio=0.75)

        assert str(cmd) == "setmem 0.75"
        assert cmd.valid is True

    def test_setcompress_basic(self):
        cmd = command.setcompress(enable=True, _type=ct.compression_type.COMPRESSION_GZIP1, quantization=16)

        assert str(cmd) == "setcompress 1 -type=gzip1 16"
        assert cmd.valid is True

    def test_set16bits(self):
        cmd = command.set16bits()

        assert str(cmd) == "set16bits"
        assert cmd.valid is True

    def test_set32bits(self):
        cmd = command.set32bits()

        assert str(cmd) == "set32bits"
        assert cmd.valid is True

    def test_setext(self):
        cmd = command.setext(extension=ct.fits_extension.FITS_EXT_FITS)

        assert str(cmd) == "setext fits"
        assert cmd.valid is True


class TestGetCommands:
    def test_get_basic(self):
        cmd = command.get(variable=ct.SirilSetting.MEM_MODE)

        assert str(cmd) == "get core.mem_mode"
        assert cmd.valid is True

    def test_get_basic_string(self):
        cmd = command.get(variable="core.mem_mode")

        assert str(cmd) == "get core.mem_mode"
        assert cmd.valid is True

    def test_get_all(self):
        cmd = command.get(list_all=True)

        assert str(cmd) == "get -a"
        assert cmd.valid is True

    def test_get_all_detailed(self):
        cmd = command.get(list_all=True, detailed=True)

        assert str(cmd) == "get -A"
        assert cmd.valid is True


class TestGetRefCommands:
    def test_getref_basic(self):
        cmd = command.getref("sequence")

        assert str(cmd) == "getref sequence"
        assert cmd.valid is True


class TestSetRefCommands:
    def test_setref_basic(self):
        cmd = command.setref("sequence", 1)

        assert str(cmd) == "setref sequence 1"
        assert cmd.valid is True


class TestUtilityCommands:
    def test_close_command(self):
        cmd = command.close()

        assert str(cmd) == "close"
        assert cmd.valid is True

    def test_exit_command(self):
        cmd = command.exit()

        assert str(cmd) == "exit"
        assert cmd.valid is True

    def test_help_command(self):
        cmd = command.help()

        assert str(cmd) == "help"
        assert cmd.valid is True

    def test_help_with_topic(self):
        cmd = command.help("load")

        assert str(cmd) == "help load"
        assert cmd.valid is True

    def test_pwd_command(self):
        cmd = command.pwd()

        assert str(cmd) == "pwd"
        assert cmd.valid is True

    def test_cd_command(self):
        cmd = command.cd("/path/to/directory")

        assert str(cmd) == "cd /path/to/directory"
        assert cmd.valid is True

    def test_cd_with_spaces(self):
        cmd = command.cd("/path with spaces/directory")

        assert str(cmd) == "cd '/path with spaces/directory'"
        assert cmd.valid is True

    def test_link_command(self):
        cmd = command.link("sequence_name")

        assert str(cmd) == "link sequence_name"
        assert cmd.valid is True

    def test_offline_command(self):
        cmd = command.offline()

        assert str(cmd) == "offline"
        assert cmd.valid is True

    def test_online_command(self):
        cmd = command.online()

        assert str(cmd) == "online"
        assert cmd.valid is True

    def test_requires_command(self):
        cmd = command.requires("1.4.2")

        assert str(cmd) == "requires 1.4.2"
        assert cmd.valid is True

    def test_capabilities_command(self):
        cmd = command.capabilities()

        assert str(cmd) == "capabilities"
        assert cmd.valid is True


class TestMetadataCommands:
    def test_dumpheader_basic(self):
        cmd = command.dumpheader()

        assert str(cmd) == "dumpheader"
        assert cmd.valid is True

    def test_jsonmetadata_basic(self):
        cmd = command.jsonmetadata("image.fits", out="output.json")

        assert str(cmd) == "jsonmetadata image.fits -out=output.json"
        assert cmd.valid is True

    def test_update_key_basic(self):
        cmd = command.update_key("KEYWORD", value="value")

        assert str(cmd) == "update_key KEYWORD value"
        assert cmd.valid is True

    def test_update_key_with_comment(self):
        cmd = command.update_key("KEYWORD", value="value", keycomment="This is a comment")

        assert str(cmd) == "update_key KEYWORD value 'This is a comment'"
        assert cmd.valid is True

    def test_update_key_delete_key(self):
        cmd = command.update_key("KEYWORD", delete=True)

        assert str(cmd) == "update_key -delete KEYWORD"
        assert cmd.valid is True

    def test_update_key_modify_key(self):
        cmd = command.update_key("KEYWORD", modify=True, new_key="NEW_KEYWORD")

        assert str(cmd) == "update_key -modify KEYWORD NEW_KEYWORD"
        assert cmd.valid is True

    def test_update_key_comment(self):
        cmd = command.update_key("KEYWORD", comment=True, keycomment="This is a comment")

        assert str(cmd) == "update_key -comment 'This is a comment'"
        assert cmd.valid is True

    def test_parse_basic(self):
        cmd = command.parse("KEYWORD")

        assert str(cmd) == "parse KEYWORD"
        assert cmd.valid is True


class TestSequenceMetadataCommands:
    def test_sequpdate_key_basic(self):
        cmd = command.sequpdate_key("sequence", "KEYWORD", value="value")

        assert str(cmd) == "sequpdate_key sequence KEYWORD value"
        assert cmd.valid is True

    def test_sequpdate_key_with_comment(self):
        cmd = command.sequpdate_key("sequence", "KEYWORD", value="value", keycomment="This is a comment")

        assert str(cmd) == "sequpdate_key sequence KEYWORD value 'This is a comment'"
        assert cmd.valid is True

    def test_sequpdate_key_delete_key(self):
        cmd = command.sequpdate_key("sequence", "KEYWORD", delete=True)

        assert str(cmd) == "sequpdate_key sequence -delete KEYWORD"
        assert cmd.valid is True

    def test_sequpdate_key_modify_key(self):
        cmd = command.sequpdate_key("sequence", "KEYWORD", modify=True, new_key="NEW_KEYWORD")

        assert str(cmd) == "sequpdate_key sequence -modify KEYWORD NEW_KEYWORD"
        assert cmd.valid is True

    def test_sequpdate_key_comment(self):
        cmd = command.sequpdate_key("sequence", "KEYWORD", comment=True, keycomment="This is a comment")

        assert str(cmd) == "sequpdate_key sequence -comment 'This is a comment'"
        assert cmd.valid is True


class TestSequenceHeaderCommands:
    def test_sequence_header_basic(self):
        cmd = command.seqheader("sequence", keywords=["KEYWORD"])

        assert str(cmd) == "seqheader sequence KEYWORD"
        assert cmd.valid is True

    def test_sequence_header_multiple_keywords(self):
        cmd = command.seqheader("sequence", keywords=["KEYWORD1", "KEYWORD2"])

        assert str(cmd) == "seqheader sequence KEYWORD1 KEYWORD2"
        assert cmd.valid is True


class TestPyScriptCommand:
    def test_pyscript_basic(self):
        cmd = command.pyscript("script.py")
        assert str(cmd) == "pyscript script.py"
        assert cmd.valid is True


class TestUnselectCommand:
    def test_unselect_basic(self):
        cmd = command.unselect("sequence", 1, 5)
        assert str(cmd) == "unselect sequence 1 5"
        assert cmd.valid is True
