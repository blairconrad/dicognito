import os
import re

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

        release_body = release_body.strip().replace("%", "%25").replace("\n", "%0A").replace("\r", "%0D")

        with open(os.environ["GITHUB_OUTPUT"], mode="a") as github_output:
            print(f"release-name={release_name}", file=github_output)
            print(f"is-prerelease={is_prerelease}", file=github_output)
            print(f"release-body={release_body}", file=github_output)
