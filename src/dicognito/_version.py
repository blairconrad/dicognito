"""dicognito - anonymize DICOM datasets."""
import re
from os.path import abspath, dirname, join

DATA_ROOT = abspath(dirname(__file__))
with open(join(DATA_ROOT, "release_notes.md")) as notes:
    for line in notes:
        if line.startswith("## "):
            __version__ = line[3:].strip()
            break

__version_info__ = tuple(re.match(r"(\d+\.\d+\.\d+).*", __version__).group(1).split("."))  # type: ignore[union-attr]
