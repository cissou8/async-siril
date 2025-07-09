test:
	uv run pytest

check:
	uv run ruff check
	@echo ""
	uv run ty check --output-format concise

format:
	uv run ruff format

generate-commands:
	cd packages/siril-command-src && uv run export_commands.py --clean
	cd packages/siril-command-src && uv run merge_commands.py ../../src/async_siril/command.py
	