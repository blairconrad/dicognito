import sys
import os.path
import shutil

from invoke import task


def add_source_to_sys_path():
    base_dir = os.path.dirname(__file__)
    path = os.path.join(base_dir, "src")
    if path not in sys.path:
        sys.path = [path] + sys.path


@task(iterable=["like"])
def test(context, like, loop=False):
    import pytest

    add_source_to_sys_path()

    args = ["tests"]
    if like:
        args += ["-k", " or ".join(like)]
    if loop:
        args += ["--looponfail"]

    pytest.main(args)


@task
def smoketest(context):
    import smoketest.smoketest

    add_source_to_sys_path()

    smoketest.smoketest.main()
    context.run(r"code --diff smoketest\original.txt smoketest\anonymized.txt")


@task
def clean(context):
    def rm(path):
        if os.path.exists(path):
            shutil.rmtree(path)

    [rm(path) for path in ("build", "dicognito.egg-info", "dist")]
