import os
import re


def set_output_parameter(name: str, value: str) -> None:
    with open(os.environ["GITHUB_OUTPUT"], mode="a") as github_output:
        print(f"{name}={value}", file=github_output)


def set_multiline_output_parameter(name: str, value: str) -> None:
    with open(os.environ["GITHUB_OUTPUT"], mode="a") as github_output:
        print(f"{name}<<END_OF_{name}", file=github_output)
        print(value, file=github_output)
        print(f"END_OF_{name}", file=github_output)


with open("src/dicognito/release_notes.md") as release_notes:
    first_line = release_notes.readline()
    if first_line.startswith("## "):
        release_name = first_line[3:].strip()

        # Adapted from PEP 440:
        # https://www.python.org/dev/peps/pep-0440/#appendix-b-parsing-version-strings-with-regular-expressions
        prerelease_regex = r"([-_\.]?(a|b|c|rc|alpha|beta|pre|preview)[-_\.]?[0-9]*)"
        is_prerelease = "true" if re.search(prerelease_regex, release_name) else "false"

        release_body = ""
        for line in release_notes.readlines():
            if line.startswith("## "):
                break
            release_body += line

        set_output_parameter("release-name", release_name)
        set_output_parameter("is-prerelease", is_prerelease)
        set_multiline_output_parameter("release-body", release_body)
