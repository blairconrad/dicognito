import os
import subprocess
import sys
from typing import Sequence


def main(args: Sequence[str]) -> None:
    if len(args) != 1:
        message = f"Usage: {sys.argv[0]} new-version"
        raise Exception(message)

    new_version = args[0]

    print("Releasing", new_version)
    tools_dir = os.path.split(__file__)[0]
    os.chdir(os.path.split(tools_dir)[0])

    main_branch = "main"
    release_notes_filename = "src/dicognito/release_notes.md"
    branch_name = "release/" + new_version

    subprocess.run(["git", "switch", main_branch])
    subprocess.run(["git", "pull", "--ff-only", "origin", main_branch])
    subprocess.run(["git", "switch", "--create", branch_name])

    with open(release_notes_filename, newline="\n") as release_notes_file:
        release_notes = release_notes_file.read()
        release_notes = f"## {new_version}\n\n{release_notes}"

    with open(release_notes_filename, "w", newline="\n") as release_notes_file:
        release_notes_file.write(release_notes)

    print(f"\nReleasing version {new_version}. Changing {release_notes_filename} like so:\n")
    subprocess.run(["git", "diff", release_notes_filename])
    response = input("\n  Proceed (y/N)? ").lower() or "n"

    if response == "y":
        pass
    elif response == "n":
        print("Update cancelled. Clean up yourself.")
        return
    else:
        print(f"Unknown response '{response}'. Aborting.")
        return

    subprocess.run(["git", "commit", "--quiet", "--message", f"Set version to {new_version}", release_notes_filename])
    subprocess.run(["git", "switch", "--quiet", main_branch])
    subprocess.run(["git", "merge", "--quiet", "--no-ff", branch_name])
    subprocess.run(["git", "branch", "--delete", "--force", branch_name])
    subprocess.run(["git", "tag", new_version])
    subprocess.run(["git", "push", "origin", new_version, main_branch])


if __name__ == "__main__":
    main(sys.argv[1:])
