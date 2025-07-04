from __future__ import annotations

import attrs as a
import structlog.stdlib
import asyncio
import cappa
import pathlib
import typing as t
import ast
import re

from dataclasses import dataclass

log = structlog.stdlib.get_logger()


@dataclass
class ClassDoc:
    name: str
    doc: str

async def extract_class_docs(file_path: pathlib.Path) -> list[ClassDoc]:
    """Extract class names and their docstrings from a Python file."""
    with open(file_path, "r") as f:
        content = f.read()
    
    tree = ast.parse(content)
    class_docs = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            doc = ast.get_docstring(node)
            # print(doc)
            if doc:
                class_docs.append(ClassDoc(node.name, doc))
            # print("-------")
    
    return class_docs

@a.define(kw_only=True, frozen=True)
class MergeSirilCommands:
    destination: t.Annotated[
        pathlib.Path,
        cappa.Arg(
            help="Destination file to write the merged command classes to",
        ),
    ]

    async def __call__(self) -> None:
        log.info("Starting merge siril scriptable commands")

        # Get the current directory
        current_dir = pathlib.Path.cwd()
        log.info(f"current dir: {current_dir}")

        # Get the generated directory
        generated_dir = current_dir / "generated"
        log.info(f"generated dir: {generated_dir}")

        # Get the generated command classes
        generated_command_classes = generated_dir / "command.py"
        log.info(f"generated command classes: {generated_command_classes}")

        # Extract class docs from generated file
        source_docs = await extract_class_docs(generated_command_classes)
        log.info(f"Found {len(source_docs)} classes in source")


        log.info("Siril commands merged")
    


def main() -> None:  # pragma: no cover
    try:
        asyncio.run(cappa.invoke_async(MergeSirilCommands))
    except Exception as e:
        log.exception("Unhandled exception")
        raise cappa.Exit("There was an error while executing", code=-1) from e


if __name__ == "__main__":
    main()
