import os.path
import shutil

from invoke import task


def add_source_to_sys_path():
    os.environ["PYTHONPATH"] = "src"


@task(iterable=["like"])
def test(context, like, loop=False):
    add_source_to_sys_path()

    args = ["pytest", "--flake8", "--black"]
    if like:
        args += ["-k", " or ".join(like)]
    if loop:
        args += ["--looponfail"]

    context.run(" ".join(args))


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
