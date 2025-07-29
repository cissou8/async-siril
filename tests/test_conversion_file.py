import pathlib
import tempfile

from async_siril.conversion_file import ConversionEntry, ConversionFile


class TestConversionEntry:
    def test_conversion_entry_creation(self):
        original = pathlib.Path("/path/to/original.fits")
        converted = pathlib.Path("/path/to/converted.fit")

        entry = ConversionEntry(original, converted)

        assert entry.original_file == original
        assert entry.converted_file == converted


class TestConversionFile:
    def test_conversion_file_init_nonexistent_file(self):
        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            temp_path = pathlib.Path(temp_file.name)

        conversion_file = ConversionFile(temp_path)

        assert conversion_file.file == temp_path
        assert conversion_file.entries == []

    def test_conversion_file_init_with_valid_file(self):
        test_content = """'original1.fits' -> 'converted1.fit'
'original2.fits' -> 'converted2.fit'
'original3.fits' -> 'converted3.fit'"""

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as temp_file:
            temp_file.write(test_content)
            temp_path = pathlib.Path(temp_file.name)

        try:
            conversion_file = ConversionFile(temp_path)

            assert conversion_file.file == temp_path
            assert len(conversion_file.entries) == 3

            assert conversion_file.entries[0].original_file == pathlib.Path("original1.fits")
            assert conversion_file.entries[0].converted_file == pathlib.Path("converted1.fit")

            assert conversion_file.entries[1].original_file == pathlib.Path("original2.fits")
            assert conversion_file.entries[1].converted_file == pathlib.Path("converted2.fit")

            assert conversion_file.entries[2].original_file == pathlib.Path("original3.fits")
            assert conversion_file.entries[2].converted_file == pathlib.Path("converted3.fit")
        finally:
            temp_path.unlink()

    def test_conversion_file_complex_paths(self):
        test_content = """'/path/with spaces/original file.fits' -> '/output/path/converted file.fit'
'/another/path/file-with-dashes.fits' -> '/output/converted-file.fit'"""

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as temp_file:
            temp_file.write(test_content)
            temp_path = pathlib.Path(temp_file.name)

        try:
            conversion_file = ConversionFile(temp_path)

            assert len(conversion_file.entries) == 2

            assert conversion_file.entries[0].original_file == pathlib.Path("/path/with spaces/original file.fits")
            assert conversion_file.entries[0].converted_file == pathlib.Path("/output/path/converted file.fit")

            assert conversion_file.entries[1].original_file == pathlib.Path("/another/path/file-with-dashes.fits")
            assert conversion_file.entries[1].converted_file == pathlib.Path("/output/converted-file.fit")
        finally:
            temp_path.unlink()

    def test_conversion_file_empty_file(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as temp_file:
            temp_file.write("")
            temp_path = pathlib.Path(temp_file.name)

        try:
            conversion_file = ConversionFile(temp_path)

            assert conversion_file.file == temp_path
            assert len(conversion_file.entries) == 0
        finally:
            temp_path.unlink()

    def test_conversion_file_malformed_content(self):
        test_content = """This is not a valid conversion file
Some random text without proper format
Another line without quotes"""

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as temp_file:
            temp_file.write(test_content)
            temp_path = pathlib.Path(temp_file.name)

        try:
            conversion_file = ConversionFile(temp_path)

            assert conversion_file.file == temp_path
            assert len(conversion_file.entries) == 0
        finally:
            temp_path.unlink()

    def test_conversion_file_mixed_valid_invalid_content(self):
        test_content = """'valid1.fits' -> 'converted1.fit'
This line is invalid
'valid2.fits' -> 'converted2.fit'
Another invalid line"""

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as temp_file:
            temp_file.write(test_content)
            temp_path = pathlib.Path(temp_file.name)

        try:
            conversion_file = ConversionFile(temp_path)

            assert len(conversion_file.entries) == 2
            assert conversion_file.entries[0].original_file == pathlib.Path("valid1.fits")
            assert conversion_file.entries[0].converted_file == pathlib.Path("converted1.fit")
            assert conversion_file.entries[1].original_file == pathlib.Path("valid2.fits")
            assert conversion_file.entries[1].converted_file == pathlib.Path("converted2.fit")
        finally:
            temp_path.unlink()

    def test_read_method_directly(self):
        test_content = """'direct1.fits' -> 'converted1.fit'
'direct2.fits' -> 'converted2.fit'"""

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as temp_file:
            temp_file.write(test_content)
            temp_path = pathlib.Path(temp_file.name)

        try:
            conversion_file = ConversionFile.__new__(ConversionFile)
            conversion_file.file = temp_path
            conversion_file.entries = []

            conversion_file.read()

            assert len(conversion_file.entries) == 2
            assert conversion_file.entries[0].original_file == pathlib.Path("direct1.fits")
            assert conversion_file.entries[0].converted_file == pathlib.Path("converted1.fit")
        finally:
            temp_path.unlink()

    def test_read_nonexistent_file_returns_none(self):
        nonexistent_path = pathlib.Path("/this/path/does/not/exist.txt")

        conversion_file = ConversionFile.__new__(ConversionFile)
        conversion_file.file = nonexistent_path
        conversion_file.entries = []

        result = conversion_file.read()

        assert result is None
        assert len(conversion_file.entries) == 0
