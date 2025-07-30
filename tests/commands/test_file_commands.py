import async_siril.command as command


class TestLoadCommand:
    def test_load_with_filename(self):
        cmd = command.load("test_image.fits")

        assert str(cmd) == "load test_image.fits"
        assert cmd.valid is True

    def test_load_with_path_containing_spaces(self):
        cmd = command.load("path with spaces/image.fits")

        assert str(cmd) == "load 'path with spaces/image.fits'"
        assert cmd.valid is True

    def test_load_with_different_extensions(self):
        extensions = [".fits", ".fit", ".tif", ".tiff", ".png"]

        for ext in extensions:
            filename = f"test_image{ext}"
            cmd = command.load(filename)
            assert str(cmd) == f"load {filename}"
            assert cmd.valid is True


class TestSaveCommands:
    def test_save_basic(self):
        cmd = command.save("output_image")

        assert str(cmd) == "save output_image"
        assert cmd.valid is True

    def test_save_with_path_spaces(self):
        cmd = command.save("path with spaces/output")

        assert str(cmd) == "save 'path with spaces/output'"
        assert cmd.valid is True

    def test_savebmp_basic(self):
        cmd = command.savebmp("output.bmp")

        assert str(cmd) == "savebmp output.bmp"
        assert cmd.valid is True

    def test_savejpg_basic(self):
        cmd = command.savejpg("output.jpg")

        assert str(cmd) == "savejpg output.jpg"
        assert cmd.valid is True

    def test_savejpg_with_quality(self):
        cmd = command.savejpg("output.jpg", quality=85)

        assert str(cmd) == "savejpg output.jpg 85"
        assert cmd.valid is True

    def test_savejxl_basic(self):
        cmd = command.savejxl("output.jxl")

        assert str(cmd) == "savejxl output.jxl"
        assert cmd.valid is True

    def test_savejxl_with_quality(self):
        cmd = command.savejxl("output.jxl", quality=90)

        assert str(cmd) == "savejxl output.jxl -quality=90"
        assert cmd.valid is True

    def test_savepng_basic(self):
        cmd = command.savepng("output.png")

        assert str(cmd) == "savepng output.png"
        assert cmd.valid is True

    def test_savepnm_basic(self):
        cmd = command.savepnm("output.pnm")

        assert str(cmd) == "savepnm output.pnm"
        assert cmd.valid is True

    def test_savetif_basic(self):
        cmd = command.savetif("output.tif")

        assert str(cmd) == "savetif output.tif"
        assert cmd.valid is True

    def test_savetif32_basic(self):
        cmd = command.savetif32("output.tif")

        assert str(cmd) == "savetif32 output.tif"
        assert cmd.valid is True

    def test_savetif8_basic(self):
        cmd = command.savetif8("output.tif")

        assert str(cmd) == "savetif8 output.tif"
        assert cmd.valid is True


class TestConvertCommand:
    def test_convert_basic(self):
        cmd = command.convert("output.fits")

        assert str(cmd) == "convert output.fits"
        assert cmd.valid is True

    def test_convert_with_path_spaces(self):
        cmd = command.convert("path with spaces/output.fits")

        assert str(cmd) == "convert 'path with spaces/output.fits'"
        assert cmd.valid is True


class TestConvertrawCommand:
    def test_convertraw_basic(self):
        cmd = command.convertraw("output.fits")

        assert str(cmd) == "convertraw output.fits"
        assert cmd.valid is True

    def test_convertraw_with_path_spaces(self):
        cmd = command.convertraw("path with spaces/output.fits")

        assert str(cmd) == "convertraw 'path with spaces/output.fits'"
        assert cmd.valid is True


class TestMergeCommand:
    def test_merge_basic(self):
        cmd = command.merge("sequence1", "sequence2", "output_sequence")

        assert str(cmd) == "merge sequence1 sequence2 output_sequence"
        assert cmd.valid is True

    def test_merge_additional(self):
        cmd = command.merge(
            "sequence1", "sequence2", "output_sequence", additional_sequences=["additional1", "additional2"]
        )

        assert str(cmd) == "merge sequence1 sequence2 additional1 additional2 output_sequence"
        assert cmd.valid is True
