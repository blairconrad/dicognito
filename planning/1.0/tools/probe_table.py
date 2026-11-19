"""
Run dicognito's default Anonymizer on every PS3.15 Table E.1-1 attribute, populated and empty.

Run from the repository root, in the project environment, so the working-tree dicognito is used:
    uv run python planning/1.0/tools/probe_table.py <confidentiality_profile_attributes.json> <out.csv>
"""

import csv
import json
import sys
import warnings
from collections import Counter
from pathlib import Path

import pydicom
from pydicom.dataset import Dataset
from pydicom.datadict import dictionary_VR, keyword_for_tag

from dicognito.anonymizer import Anonymizer

warnings.simplefilter("ignore")

table_path = Path(sys.argv[1])
out_csv = Path(sys.argv[2])
rows = json.loads(table_path.read_text(encoding="utf-8"))

SAMPLE = {
    "PN": "DOE^JOHN", "LO": "SAMPLE LO", "SH": "SAMPLESH", "CS": "SAMPLE", "DA": "20200102",
    "TM": "123456", "DT": "20200102123456", "UI": "1.2.3.4.5", "AS": "045Y", "DS": "1.5", "IS": "3",
    "US": 1, "UL": 1, "SS": 1, "SL": 1, "FD": 1.0, "FL": 1.0, "OB": b"\x01\x02", "OW": b"\x01\x02",
    "UN": b"\x01\x02", "UT": "sample text", "LT": "sample text", "ST": "sample text", "UC": "sample",
    "AE": "SAMPLEAE", "UR": "http://example.org/x", "AT": 0x00100010, "OF": b"\x00\x00\x00\x00",
    "OD": b"\x00" * 8, "OL": b"\x00" * 4, "OV": b"\x00" * 8, "SV": 1, "UV": 1,
}


def make_value(vr):
    vr = vr.split(" or ")[0]
    if vr == "SQ":
        item = Dataset()
        item.CodeValue = "X"
        return vr, [item]
    return vr, SAMPLE.get(vr)


def run(tag, vr, value):
    ds = Dataset()
    ds.ensure_file_meta()
    ds.add_new(tag, vr, value)
    before = ds[tag].value
    before_repr = repr(before) if vr != "SQ" else "SQ"
    try:
        Anonymizer(seed="probe").anonymize(ds)
    except Exception as e:  # noqa: BLE001
        return f"ERROR {type(e).__name__}: {e}"[:120], ds
    if tag not in ds:
        return "removed", ds
    after = ds[tag].value
    if vr == "SQ":
        return "kept (items walked)", ds
    if after == before:
        return "unchanged", ds
    if after in ("", None, b""):
        return "emptied", ds
    return f"changed -> {after!r}"[:80], ds


results = []
counts = Counter()
for row in rows:
    raw = row["tag"].strip("()").replace(",", "")
    if len(raw) != 8 or any(c not in "0123456789abcdefABCDEF" for c in raw):
        results.append({**row, "keyword": "", "vr": "", "populated": "WILDCARD (not probed)", "empty": "", "added": ""})
        continue
    tag = int(raw, 16)
    keyword = keyword_for_tag(tag)
    try:
        vr = dictionary_VR(tag)
    except KeyError:
        results.append({**row, "keyword": "", "vr": "", "populated": "NOT IN PYDICOM DICT", "empty": "", "added": ""})
        continue
    vr1, value = make_value(vr)
    populated, ds_p = run(tag, vr1, value)
    empty_value = [] if vr1 == "SQ" else ("" if isinstance(value, str) else None)
    empty, ds_e = run(tag, vr1, empty_value)
    if vr1 == "SQ":
        empty = "removed" if tag not in ds_e else "kept"
    added = sorted(keyword_for_tag(t) or str(t) for t in ds_p.keys() if t != tag)
    results.append({**row, "keyword": keyword, "vr": vr, "populated": populated, "empty": empty, "added": ";".join(added)})
    counts[populated.split(" ->")[0].split(":")[0]] += 1

fields = ["id", "keyword", "name", "vr", "basicProfile", "rtnLongFullDatesOpt", "rtnLongModifDatesOpt",
          "rtnPatCharsOpt", "rtnDevIdOpt", "rtnInstIdOpt", "rtnUIDsOpt", "rtnSafePrivOpt", "cleanDescOpt",
          "cleanStructContOpt", "cleanGraphOpt", "stdCompIOD", "retired", "populated", "empty", "added"]
with out_csv.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
    w.writeheader()
    w.writerows(results)

print("table rows:", len(rows), "results:", len(results))
print("columns seen:", sorted({k for r in rows for k in r}))
print(counts.most_common())
