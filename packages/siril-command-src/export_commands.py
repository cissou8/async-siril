from __future__ import annotations

import attrs as a
import structlog.stdlib
import asyncio
import cappa
import pathlib
import typing as t
import subprocess
import shutil
import re

from dataclasses import dataclass

log = structlog.stdlib.get_logger()


@dataclass
class CommandInfo:
    name: str
    scriptable: bool
    includes: t.List[str]
    documentation: str

    @classmethod
    def from_file(
        cls,
        name: str,
        scriptable: bool,
        includes: t.List[str],
        base_dir: pathlib.Path,
    ) -> CommandInfo:
        """Create a CommandInfo from file paths."""

        documentation = ""

        for include in includes:
            # Load and process the main documentation
            doc_path = base_dir / include
            if not doc_path.exists():
                log.warning(f"Main documentation file not found: {doc_path}")
            else:
                with open(doc_path, "r") as f:
                    content = f.read()
                    # Remove leading '| ' from each line
                    include_doc = re.sub(r"^\|\s", "", content, flags=re.MULTILINE)
                    # Clean up any extra whitespace
                    include_doc = include_doc.strip()
                    documentation += include_doc
                    documentation += "\n\n"

        return cls(
            name=name,
            scriptable=scriptable,
            includes=includes,
            documentation=documentation,
        )


@a.define(kw_only=True, frozen=True)
class ExportSirilCommands:
    clean: t.Annotated[
        bool,
        cappa.Arg(
            short=True,
            default=False,
            help="Clean the output directory before exporting",
        ),
    ]

    async def __call__(self) -> None:
        log.info("Starting export siril scriptable commands")

        # Get the current directory
        current_dir = pathlib.Path(__file__).parent
        log.info(f"current dir: {current_dir}")

        # Get the output directory
        doc_dir = self._make_doc_dir(current_dir)

        # Get the generated directory
        generated_dir = self._make_generated_dir(current_dir)

        if not (doc_dir / "siril-doc-1.4").exists():
            log.info("Downloading and unzipping docs")
            # Download and unzip the docs for processing
            subprocess.run(
                [
                    "curl",
                    "https://gitlab.com/free-astro/siril-doc/-/archive/1.4/siril-doc-1.4.zip",
                    "-o",
                    f"{doc_dir}/siril-doc-1.4.zip",
                ]
            )
            subprocess.run(["unzip", f"{doc_dir}/siril-doc-1.4.zip", "-d", doc_dir])

        commands = self.parse_commands(doc_dir / "siril-doc-1.4" / "doc" / "Commands.rst")
        log.info(f"Parsed {len(commands)} commands")

        # Filter out non-scriptable commands
        scriptable_commands = [cmd for cmd in commands if cmd.scriptable]
        log.info(f"Filtered to {len(scriptable_commands)} scriptable commands")

        log.info(scriptable_commands[0])

        # Generate and write command classes for scriptable commands
        command_classes = []
        for cmd in scriptable_commands:
            command_classes.append(self.generate_command_class(cmd))

        # Write to command.py file
        output_file = generated_dir / "command.py"
        with open(output_file, "w") as f:
            # Write each command class
            for cmd_class in command_classes:
                f.write(cmd_class)
                f.write("\n\n")

        log.info(f"Generated command classes to {output_file}")

        log.info("Siril commands exported")

    def _make_doc_dir(self, current_dir: pathlib.Path):
        doc_dir = current_dir / "siril-doc"
        log.info(f"doc dir: {doc_dir}")

        if self.clean and doc_dir.exists():
            log.info("Cleaning doc directory")
            shutil.rmtree(doc_dir)

        if not doc_dir.exists():
            doc_dir.mkdir(parents=True, exist_ok=True)

        return doc_dir

    def _make_generated_dir(self, current_dir: pathlib.Path):
        generated_dir = current_dir / "generated"
        log.info(f"generated dir: {generated_dir}")

        if not generated_dir.exists():
            generated_dir.mkdir(parents=True, exist_ok=True)

        return generated_dir

    def parse_commands(self, commands_file: pathlib.Path) -> t.List[CommandInfo]:
        """Parse the commands file and extract command information."""
        commands = []
        with open(commands_file, "r") as f:
            content = f.read()

            # Split by command blocks
            blocks = content.split(".. command:: ")
            # print(len(blocks))
            # for block in blocks[1:5]:
            #     print(block.rstrip())
            #     print('----------------')

            for block in blocks[1:]:  # Skip first empty block
                # Extract command name and scriptable flag
                match = re.search(r"([^\n]+)\n   :scriptable: ([01])", block)
                if not match:
                    continue

                name = match.group(1).strip()
                scriptable = bool(int(match.group(2)))

                # Extract include directives
                includes = re.findall(r".. include:: ([^\n]+)", block)
                includes = [include.strip() for include in includes]

                commands.append(
                    CommandInfo.from_file(
                        name=name,
                        scriptable=scriptable,
                        includes=includes,
                        base_dir=commands_file.parent,
                    )
                )

        return commands

    def generate_command_class(self, cmd: CommandInfo) -> str:
        """Generate a Python class for a command."""
        # Clean the command name to be a valid Python class name
        class_name = cmd.name.replace("-", "_").replace(".", "_")

        # Format the documentation and usage strings
        doc_lines = cmd.documentation.split("\n")

        # Combine documentation and usage with a separator
        doc_string = "".join(f"    {line}\n" for line in doc_lines)

        return f"""class {class_name}(BaseCommand):
    \"\"\"
{doc_string.rstrip()}
    \"\"\"
"""


def main() -> None:  # pragma: no cover
    try:
        asyncio.run(cappa.invoke_async(ExportSirilCommands))
    except Exception as e:
        log.exception("Unhandled exception")
        raise cappa.Exit("There was an error while executing", code=-1) from e


if __name__ == "__main__":
    main()
