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

Two tests compare anonymization output with committed expected files. `tests/test_seeded_output.py` anonymizes a rich dataset with a fixed seed and compares the result with `tests/seeded_output.expected.json`, which lists every element of the input and output with what anonymization did to it (changed, emptied, removed, added or kept) and its resulting value. `tests/test_ps315_output.py` anonymizes a minimal dataset for each attribute of DICOM PS3.15 Table E.1-1 (listed in `tests/ps315_table_2024b.json`, a pinned copy of the DICOM 2024b table that the test never downloads), once with a populated value and once with an empty one, and compares the actions and values with `tests/ps315_output.expected.json`, which has one line per attribute.

When the output differs, the test writes it to a matching `.actual.json` file (for example `tests/seeded_output.actual.json`, ignored by git) and fails. Compare the two files, for example with `code --diff tests/seeded_output.expected.json tests/seeded_output.actual.json`, and copy the intended changes into the `.expected.json` file, or copy the whole `.actual.json` over it if every change is intended. The `.actual.json` file is deleted the next time the test passes.

Commit the updated expected files with the change that caused them, and describe the output change in the release notes.
