"""Run all tests."""

import subprocess


def run_command(command: list[str]) -> None:
    """Run a command using subprocess. Raise an error if the command has a non-zero exit code."""
    subprocess.run(check=True, args=command)


def main() -> None:
    """Run all tests."""
    commands = [
        ["ruff", "format", "--check", "."],
        ["ruff", "check"],
        ["mypy", "src", "tests"],
        ["pytest"],
    ]

    for command in commands:
        run_command(command)


if __name__ == "__main__":
    main()
