# SIRIL Command Source

This tool contains the logic to donwload the Siril documentation and generate the command classes for the scriptable commands.

## Usage

First navigate to the directory containing the source code.
```bash
cd packages/siril-command-src
```

Generate the command classes first to the generated directory.
```bash
uv run export_commands.py
```

Then merge the command classes into a single file.
```bash
uv run merge_commands.py ../../src/async_siril/command.py
```

The command classes will be written to the `async_siril/command.py` file.

Since the source code is version controllered, you can now review the changes and commit them.