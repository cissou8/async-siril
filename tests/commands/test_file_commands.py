from async_siril.command import (
    load,
    save,
    savebmp,
    savejpg,
    savejxl,
    savepng,
    savepnm,
    savetif,
    savetif32,
    savetif8,
    convert,
    convertraw,
    merge,
)


class TestLoadCommand:
    def test_load_with_filename(self):
        cmd = load("test_image.fits")

        assert str(cmd) == "load test_image.fits"
        assert cmd.valid is True

    def test_load_with_path_containing_spaces(self):
        cmd = load("path with spaces/image.fits")

        assert str(cmd) == "load 'path with spaces/image.fits'"
        assert cmd.valid is True

    def test_load_with_different_extensions(self):
        extensions = [".fits", ".fit", ".tif", ".tiff", ".png"]

        for ext in extensions:
            filename = f"test_image{ext}"
            cmd = load(filename)
            assert str(cmd) == f"load {filename}"
            assert cmd.valid is True


class TestSaveCommands:
    def test_save_basic(self):
        cmd = save("output_image")

        assert str(cmd) == "save output_image"
        assert cmd.valid is True

    def test_save_with_path_spaces(self):
        cmd = save("path with spaces/output")

        assert str(cmd) == "save 'path with spaces/output'"
        assert cmd.valid is True

    def test_savebmp_basic(self):
        cmd = savebmp("output.bmp")

        assert str(cmd) == "savebmp output.bmp"
        assert cmd.valid is True

    def test_savejpg_basic(self):
        cmd = savejpg("output.jpg")

        assert str(cmd) == "savejpg output.jpg"
        assert cmd.valid is True

    def test_savejpg_with_quality(self):
        cmd = savejpg("output.jpg", quality=85)

        assert str(cmd) == "savejpg output.jpg 85"
        assert cmd.valid is True

    def test_savejxl_basic(self):
        cmd = savejxl("output.jxl")

        assert str(cmd) == "savejxl output.jxl"
        assert cmd.valid is True

    def test_savejxl_with_quality(self):
        cmd = savejxl("output.jxl", quality=90)

        assert str(cmd) == "savejxl output.jxl -quality=90"
        assert cmd.valid is True

    def test_savepng_basic(self):
        cmd = savepng("output.png")

        assert str(cmd) == "savepng output.png"
        assert cmd.valid is True

    def test_savepnm_basic(self):
        cmd = savepnm("output.pnm")

        assert str(cmd) == "savepnm output.pnm"
        assert cmd.valid is True

    def test_savetif_basic(self):
        cmd = savetif("output.tif")

        assert str(cmd) == "savetif output.tif"
        assert cmd.valid is True

    def test_savetif32_basic(self):
        cmd = savetif32("output.tif")

        assert str(cmd) == "savetif32 output.tif"
        assert cmd.valid is True

    def test_savetif8_basic(self):
        cmd = savetif8("output.tif")

        assert str(cmd) == "savetif8 output.tif"
        assert cmd.valid is True


class TestConvertCommand:
    def test_convert_basic(self):
        cmd = convert("output.fits")

        assert str(cmd) == "convert output.fits"
        assert cmd.valid is True

    def test_convert_with_path_spaces(self):
        cmd = convert("path with spaces/output.fits")

        assert str(cmd) == "convert 'path with spaces/output.fits'"
        assert cmd.valid is True


class TestConvertrawCommand:
    def test_convertraw_basic(self):
        cmd = convertraw("output.fits")

        assert str(cmd) == "convertraw output.fits"
        assert cmd.valid is True

    def test_convertraw_with_path_spaces(self):
        cmd = convertraw("path with spaces/output.fits")

        assert str(cmd) == "convertraw 'path with spaces/output.fits'"
        assert cmd.valid is True


class TestMergeCommand:
    def test_merge_basic(self):
        cmd = merge("sequence1", "sequence2", "output_sequence")

        assert str(cmd) == "merge sequence1 sequence2 output_sequence"
        assert cmd.valid is True

    def test_merge_additional(self):
        cmd = merge("sequence1", "sequence2", "output_sequence", additional_sequences=["additional1", "additional2"])

        assert str(cmd) == "merge sequence1 sequence2 additional1 additional2 output_sequence"
        assert cmd.valid is True
