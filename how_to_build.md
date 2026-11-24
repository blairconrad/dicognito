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

## Updating the expected anonymization output

Two tests compare anonymization output with committed expected files. `tests/test_seeded_output.py` anonymizes a rich dataset with a fixed seed and compares the result with `tests/expected_seeded_output.json`, which lists every element of the input and output with what anonymization did to it (changed, emptied, removed, added or kept) and its resulting value. `tests/test_ps315_output.py` anonymizes a minimal dataset for each attribute of DICOM PS3.15 Table E.1-1 (listed in `tests/ps315_table_2024b.json`, a pinned copy of the DICOM 2024b table that the test never downloads), once with a populated value and once with an empty one, and compares the actions and values with `tests/expected_ps315_output.json`, which has one line per attribute. When a change is meant to alter this output, update the expected files by running the tests with `DICOGNITO_UPDATE_EXPECTED_OUTPUT` set. A test rewrites its file and then fails on purpose, so the update can't pass unnoticed:

```powershell
$env:DICOGNITO_UPDATE_EXPECTED_OUTPUT = 1; uv run pytest tests/test_seeded_output.py tests/test_ps315_output.py; Remove-Item Env:DICOGNITO_UPDATE_EXPECTED_OUTPUT
```

```bash
DICOGNITO_UPDATE_EXPECTED_OUTPUT=1 uv run pytest tests/test_seeded_output.py tests/test_ps315_output.py
```

Review the diff of the expected files, commit them with the change that caused it, and describe the output change in the release notes.
