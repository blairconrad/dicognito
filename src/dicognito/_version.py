"""dicognito - anonymize DICOM datasets"""
from os.path import abspath, dirname, join
import re

DATA_ROOT = abspath(dirname(__file__))
with open(join(DATA_ROOT, "release_notes.md"), "r") as notes:
    for line in notes:
        if line.startswith("## "):
            __version__ = line[3:].strip()
            break

__version_info__ = tuple(re.match(r"(\d+\.\d+\.\d+).*", __version__).group(1).split("."))
