[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

# async-siril

Async Siril is an asyncio based python wrapper around [Siril 1.4.0](https://www.siril.org/) used for processing astronomy data for astrophotography and science. The library provides a pythonic interface to the Siril command line interface and all of it's commands. Scripts, processes, and workflows can be built with modern async python.

## Features

* async/await based using [asyncio](https://docs.python.org/3/library/asyncio.html)
* code generated Siril commands from [free-astro/siril-doc](https://gitlab.com/free-astro/siril-doc/)
* logging with [structlog](https://www.structlog.org/)
* example CLI commands built for calibration, registration & stacking workflows [examples](./examples)
* some helpers for common logic (see `async_siril.helpers`)
* minimal dependencies (`asyncio`, `structlog`, `psutil`, `attrs`)
* Linux, Mac, & Windows support

## Requirements

* Siril installed on your system (https://www.siril.org/)
* Python 3.12 or higher
* [uv](https://docs.astral.sh/uv/) or [pip](https://pip.pypa.io/en/stable/)

## Installation

```bash
uv add async-siril
# OR
pip install async-siril
```

## Usage

Here is a simple example of how to create a master bias using the library:

```python
import asyncio
import pathlib

from async_siril import SirilCli
from async_siril.command import setext, set32bits, convert, stack
from async_siril.command_types import fits_extension

async def main():
    current_dir = pathlib.Path(__file__).parent
    async with SirilCli(directory=current_dir) as siril:
        await siril.command(setext(fits_extension.FITS_EXT_FIT))
        await siril.command(set32bits())

        await siril.command(convert("bias"))
        await siril.command(stack("bias", out="bias_master"))

if __name__ == "__main__":
    asyncio.run(main())
```

You are not required to use the Siril CLI commands and if you know what you are doing, you can use the library to run any command you want.

```python
from async_siril import SirilCli

async def main():
    async with SirilCli() as siril:
        await siril.command("setext fits")
        await siril.command("set32bits")
        await siril.command("convert bias")
        await siril.command("stack bias bias_master")

if __name__ == "__main__":
    asyncio.run(main())
```

By default, any command that fails will throw an exception and shut things down. If you want to catch these types of errors and try again or handle a different way you can use the `failable_command` method.

```python
from async_siril import SirilCli

async def main():
    async with SirilCli() as siril:
        await siril.command("setext fits")
        await siril.command("set32bits")
        await siril.command("convert bias")
        result = await siril.failable_command("stack bias bias_master")
        if not result:
            print("Stack failed, make a change and try again")

if __name__ == "__main__":
    asyncio.run(main())
```


## Roadmap

### Immediate
* [x] smart source the siril cli
* [x] setup logging correctly
* [x] async examples with cappa
* [x] full on command listing
* [x] automated command coverage checking
* [x] review all python commands and their types (see "TODO:")
* [x] pytest setup for common commands
* [x] updated examples with how to
* [x] make flats cli example
* [x] add type check with `ty` tool
* [x] make linear stack cli example
* [x] logging cleanup and namespaces
* [x] updated readme with how to
* [x] How to contribute
* [x] Confirm Linux & Windows support
* [x] Updated LICENSE
* [ ] Gitops / CI / CD
* [ ] publish step to PyPI

### Future
* [ ] multi process support (named pipes need to be dynamic, only available on Linux)
* [ ] developer docs
* [ ] make rgb cli example
* [ ] clean up the command & types import signatures to be less verbose
* [ ] multi process examples (ex. stack by filter in parallel by process)
* [ ] exposing cgroup aware startup (for support in containerized environments)
* [ ] base container image usage with Siril pre-installed
* [ ] multiple siril version support (how to with generated commands)
* [ ] additional composit helpers or commands to reduce boilerplate repetition and provide best practices
* [ ] More test coverage and coverage reporting

## Contributing

PRs are welcome & appreciated! See the [contributing guide](./CONTRIBUTING.md) to get started.

## FAQ

#### Why not use [pysiril](https://gitlab.com/free-astro/pysiril)?

[pysiril](https://gitlab.com/free-astro/pysiril) is a great library for interacting with Siril. However, it is not asyncio based and does not provide a pythonic interface to the Siril command line interface.

#### Siril just added python scripts, how is this different?

The new python scripts added to Siril are a great addition for in app scripts and can do a lot of powerful things. However, sometimes you just need a simple interface for headless operations of Siril.

## Acknowledgements

Siril is a fantastic piece of software and am grateful to the [free-astro](https://gitlab.com/free-astro) team for their hard work. And a special thanks to [Vincent](https://gitlab.com/Vincent-FA) for answering questions and providing support.

## License

async-siril is licensed under either of

- Apache License, Version 2.0, ([LICENSE-APACHE](LICENSE-APACHE) or
  <https://www.apache.org/licenses/LICENSE-2.0>)
- MIT license ([LICENSE-MIT](LICENSE-MIT) or <https://opensource.org/licenses/MIT>)

at your option.

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in async-siril by you, as defined in the Apache-2.0 license, shall be dually licensed as above, without any additional terms or conditions.