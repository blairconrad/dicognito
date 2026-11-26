"""Duties for testing, formatting, linting, and type checking."""

import sys
from inspect import currentframe, getdoc, getframeinfo
from os import environ

from duty import duty
from duty.context import Context

# duty prints "✓"; redirected output on Windows defaults to cp1252 before Python 3.15 and would crash.
sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[union-attr]


def _title() -> str:
    return getdoc(globals()[getframeinfo(currentframe().f_back).function])


@duty
def test(ctx: Context) -> None:
    """Run the tests."""
    # for now, do not capture output, since it hides warnings; once we fix the warnings, remove this and treat warnings as errors
    ctx.run(["pytest", "--color", "auto" if environ.get("CI") == "true" else "yes", "."], title=_title(), capture=False)


@duty
def format(ctx: Context) -> None:  # noqa: A001 - shadowing built-in function name is safe here
    """Format files."""
    ctx.run(["ruff", "format", "."], title=_title())


@duty
def check_format(ctx: Context) -> None:
    """Check format."""
    ctx.run(["ruff", "format", "--check", "."], title=_title())


@duty
def check_style(ctx: Context) -> None:
    """Check style."""
    ctx.run(["ruff", "check"], title=_title())


@duty
def check_types(ctx: Context) -> None:
    """Check types."""
    ctx.run(["mypy", "src", "tests"], title=_title())


@duty(pre=[check_format, check_style, check_types])
def check(ctx: Context) -> None:
    """Check everything short of running the tests."""


@duty(pre=[check, test])
def ci(ctx: Context) -> None:
    """Check everything, including the tests. In theory if this passes, we can release."""
