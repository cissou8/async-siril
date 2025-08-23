from __future__ import annotations

import attrs as a
import structlog.stdlib
import asyncio
import cappa
import pathlib
import typing as t
import re

log = structlog.stdlib.get_logger()


def extract_class_docs(source_text: str) -> dict[str, str]:
    """
    Extracts class definitions with their docstrings.
    Returns a dict: { 'class ClassName(Base...)': full_text_block }
    """
    class_blocks = {}
    # Match classes with docstrings: triple quotes (""" or ''')
    pattern = re.compile(r'((class\s+\w+\s*\(.*?\):)\n\s+r"""(?:.|\n)*?""")', re.MULTILINE)

    for match in pattern.finditer(source_text):
        block = match.group(1)
        class_def_line = match.group(2)
        class_blocks[class_def_line] = block

    return class_blocks


def replace_docstrings(
    destination_text: str, class_docs: dict[str, str]
) -> tuple[str, list[str], list[str], list[str]]:
    """
    Replaces docstrings in destination_text using entries from class_docs.
    Returns the updated destination text and a list of missing classes.
    """

    # Classes that are in the destination but not source (need to remove manually)
    removed_classes = []

    # Classes that are in both (need to replace)
    updated_classes = []

    def replacer(match) -> str:
        # print(match.group(2))
        class_def_line = match.group(2)
        if class_def_line in class_docs:
            # print(f"Found {class_def_line}")
            updated_classes.append(class_def_line)
            return class_docs[class_def_line]
        else:
            removed_classes.append(class_def_line)
            return match.group(0)

    pattern = re.compile(r'((class\s+\w+\s*\(.*?\):)\n\s+r"""(?:.|\n)*?""")', re.MULTILINE)
    new_text = pattern.sub(replacer, destination_text)

    # Classes that are in the source but not destination (need to add manually)
    new_classes = list(set(class_docs.keys()) - set(updated_classes))

    return new_text, new_classes, removed_classes, updated_classes


@a.define(kw_only=True, frozen=True)
class MergeSirilCommands:
    destination: t.Annotated[
        pathlib.Path,
        cappa.Arg(
            help="Destination file to write the merged command classes to",
        ),
    ] = pathlib.Path("../../src/async_siril/command.py")

    async def __call__(self) -> None:
        log.info("Starting merge siril scriptable commands")

        # Get the current directory
        current_dir = pathlib.Path(__file__).parent
        log.info(f"current dir: {current_dir}")

        # Get the generated directory
        generated_dir = current_dir / "generated"
        log.info(f"generated dir: {generated_dir}")

        # Get the generated command classes
        generated_command_classes = generated_dir / "command.py"
        log.info(f"generated command classes: {generated_command_classes}")

        # Extract class docs from generated file
        source_text = generated_command_classes.read_text()
        source_docs = extract_class_docs(source_text)
        log.info(f"Found {len(source_docs)} classes in source")

        # Update the destination file
        destination_text = self.destination.read_text()
        updated_text, new_classes, removed_classes, updated_classes = replace_docstrings(destination_text, source_docs)
        log.info(f"Destination text changed: {updated_text != destination_text}")

        # Write updated file
        self.destination.write_text(updated_text)
        if new_classes:
            log.warning(f" {len(new_classes)} Classes found in source but missing in destination:")
            for cls in new_classes:
                log.warning(f" - {cls}")
        if removed_classes:
            log.warning(f" {len(removed_classes)} Classes found in destination but missing in source:")
            for cls in removed_classes:
                log.warning(f" - {cls}")

        log.info(f"Updated {len(updated_classes)} classes")
        log.info("Siril commands merged")


def main() -> None:  # pragma: no cover
    try:
        asyncio.run(cappa.invoke_async(MergeSirilCommands))
    except Exception as e:
        log.exception("Unhandled exception")
        raise cappa.Exit("There was an error while executing", code=-1) from e


if __name__ == "__main__":
    main()
