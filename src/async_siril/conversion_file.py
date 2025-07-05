import re
import pathlib
import typing as t
import structlog.stdlib
from dataclasses import dataclass

log = structlog.stdlib.get_logger()


@dataclass
class ConversionEntry:
    original_file: pathlib.Path
    converted_file: pathlib.Path


@dataclass
class ConversionFile:
    entries: t.List[ConversionEntry]
    file: pathlib.Path

    def __init__(self, file: pathlib.Path):
        self.file = file
        self.entries = []
        self.read()

    def read(self):
        if not self.file.exists():
            return None

        regex = r"'(.*?)'.*?'(.*?)'"
        with open(self.file) as txt_file:
            raw = txt_file.read()
            matches = re.finditer(regex, raw, re.MULTILINE)
            for _match_num, match in enumerate(matches, start=1):
                orig_file = pathlib.Path(match.group(1))
                conv_file = pathlib.Path(match.group(2))

                self.entries.append(ConversionEntry(orig_file, conv_file))
