"""Duties for testing, formatting, linting, and type checking."""

from inspect import currentframe, getdoc, getframeinfo
from os import environ

from duty import duty
from duty.context import Context


def _title() -> str:
    return getdoc(globals()[getframeinfo(currentframe().f_back).function])


@duty
def test(ctx: Context) -> None:
    """Run the tests."""
    ctx.run(["pytest", "--color", "auto" if environ.get("CI") == "true" else "yes"], title=_title())


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
