# How to build

## Prerequisites

Ensure that the following are installed:

* [uv](https://docs.astral.sh/uv/#uv)

## Building

From a command prompt in the root of the repo, run

```powershell
uv run test.py
```

This will build a source distribution and run tests as is done on the continuous integration server.
It's the best way to ensure that any changes you make will work on the server.
The tests will be run on the lowest supported python version.
If you wish to run with a particular Python version, use uv's `--python` flag to select it:

```powershell
uv run --python 3.12 test.py
```
