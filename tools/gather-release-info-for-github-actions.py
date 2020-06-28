import re

with open("src/dicognito/release_notes.md", "r") as release_notes:
    first_line = release_notes.readline()
    if first_line.startswith("## "):
        release_name = first_line[3:].strip()

        # Adapted from PEP 440:
        # https://www.python.org/dev/peps/pep-0440/#appendix-b-parsing-version-strings-with-regular-expressions
        prerelease_regex = r"([-_\.]?(a|b|c|rc|alpha|beta|pre|preview)[-_\.]?[0-9]*)"
        if re.search(prerelease_regex, release_name):
            is_prerelease = "true"
        else:
            is_prerelease = "false"

        release_body = ""
        for line in release_notes.readlines():
            if line.startswith("## "):
                break
            release_body += line

        release_body = release_body.strip().replace("%", "%25").replace("\n", "%0A").replace("\r", "%0D")

        print(f"::set-output name=release-name::{release_name}")
        print(f"::set-output name=is-prerelease::{is_prerelease}")
        print(f"::set-output name=release-body::{release_body}")
