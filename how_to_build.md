# How to build

At the time of writing the build is only confirmed to work on Windows.

## Prerequisites

Ensure that the following are installed:

* tox - version 3.7.0 is confirmed to work, but others may as well

## Building

From a command prompt in the root of the repo, run

```powershell
tox
```

This will build a source distribution and run tests in all supported environments. This replicates the
testing done on the continuous integration server, and is the best way to ensure that any changes you make
will work on the server. If you lack any environments and cannot install them, use the `-e` flag to limit
your test run to those that you do have.

## Extras

The `build.ps1` file in the root of the directory contains some convenience targets that can be used to
do a quick (quicker than the full test run) check that your changes are working. The supplied commands may
change at any time, without notice. `.\build.ps1 help` will list the available targets, which may require
that certain additional prerequisites (e.g. pytest) be installed.