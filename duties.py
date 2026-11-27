"""Duties for testing, formatting, linting, and type checking."""

import shutil
import sys
from os import environ
from pathlib import Path

from duty import duty
from duty.context import Context

# duty prints "✓"; redirected output on Windows defaults to cp1252 before Python 3.15 and would crash.
sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[union-attr]


@duty
def test(ctx: Context) -> None:
    """Run the tests."""
    # for now, do not capture output, since it hides warnings; once we fix the warnings, remove this and treat warnings as errors
    ctx.run(
        ["pytest", "--color", "auto" if environ.get("CI") == "true" else "yes"], title="Run the tests.", capture=False
    )


@duty
def format(ctx: Context) -> None:  # noqa: A001 - shadowing built-in function name is safe here
    """Format files."""
    ctx.run(["ruff", "format", "."], title="Format files.")


@duty
def check_format(ctx: Context) -> None:
    """Check format."""
    ctx.run(["ruff", "format", "--check", "."], title="Check format.")


@duty
def check_style(ctx: Context) -> None:
    """Check style."""
    ctx.run(["ruff", "check"], title="Check style.")


@duty
def check_types(ctx: Context) -> None:
    """Check types."""
    ctx.run(["mypy", "src", "tests"], title="Check types.")


@duty
def fix(ctx: Context) -> None:
    """Fix style problems and format files."""
    ctx.run(["ruff", "check", "--fix"], title="Fix style.")
    ctx.run(["ruff", "format", "."], title="Format files.")


@duty
def accept_output(ctx: Context) -> None:  # noqa: ARG001 - duties must accept a context
    """Accept the output of failed expected-output tests as the new expected output."""
    actual_files = sorted(Path("tests").glob("*.actual.json"))
    for actual in actual_files:
        shutil.copyfile(actual, actual.with_name(actual.name.replace(".actual.json", ".expected.json")))
    print(f"Accepted {len(actual_files)} actual output file(s).")


@duty(pre=[check_format, check_style, check_types])
def check(ctx: Context) -> None:
    """Check everything short of running the tests."""


@duty(pre=[check, test])
def ci(ctx: Context) -> None:
    """Check everything, including the tests. In theory if this passes, we can release."""
