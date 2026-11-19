# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Summarize the CSV written by probe_table.py. Usage: uv run planning/1.0/tools/analyze_probe.py <probe.csv>"""

import csv
import sys
from collections import Counter, defaultdict

rows = list(csv.DictReader(open(sys.argv[1], encoding="utf-8")))
print("rows", len(rows))


def outcome(r):
    p = r["populated"]
    for k in ("changed", "unchanged", "removed", "emptied", "kept (items walked)", "WILDCARD", "NOT IN", "ERROR"):
        if p.startswith(k):
            return k
    return p


xt = Counter((r["basicProfile"], outcome(r)) for r in rows)
codes = sorted({r["basicProfile"] for r in rows})
outs = sorted({outcome(r) for r in rows})
print("| basic \\ dicognito | " + " | ".join(outs) + " |")
for c in codes:
    print(f"| {c} | " + " | ".join(str(xt[(c, o)]) for o in outs) + " |")

print("\n## Empty-value outcomes (non-SQ)")
print(Counter(r["empty"].split(" ->")[0] for r in rows if r["vr"] != "SQ" and outcome(r) not in ("WILDCARD", "NOT IN")))
print("\n## Empty becomes populated:")
for r in rows:
    if r["empty"].startswith("changed"):
        print(" ", r["keyword"], r["vr"], r["empty"])
print("\n## Elements added when populated:")
for r in rows:
    if r["added"]:
        print(" ", r["keyword"], "->", r["added"])
print("\n## Wildcard / not-in-dict rows:")
for r in rows:
    if outcome(r) in ("WILDCARD", "NOT IN"):
        print(" ", r["id"], r["name"], r["basicProfile"], r["populated"])

print("\n## Unchanged (non-K basic), with option columns, grouped by VR")
by_vr = defaultdict(list)
for r in rows:
    if outcome(r) == "unchanged" and r["basicProfile"] != "K":
        opts = ",".join(f"{k}={r[k]}" for k in ("rtnLongModifDatesOpt", "rtnPatCharsOpt", "rtnDevIdOpt", "rtnInstIdOpt", "cleanDescOpt", "cleanStructContOpt", "cleanGraphOpt", "rtnSafePrivOpt", "rtnUIDsOpt") if r[k])
        by_vr[r["vr"]].append(f'{r["keyword"]} ({r["id"]}) basic={r["basicProfile"]} retired={r.get("retired","")} {opts}')
for vr in sorted(by_vr):
    print(f"\n### {vr} ({len(by_vr[vr])})")
    for line in by_vr[vr]:
        print("  ", line)

print("\n## Changed but basic says K or C (dicognito more aggressive / different)")
for r in rows:
    if outcome(r) in ("changed", "removed", "emptied") and r["basicProfile"] in ("K", "C"):
        print(" ", r["keyword"], r["basicProfile"], r["populated"])
print("\n## Removed by dicognito")
for r in rows:
    if outcome(r) == "removed":
        print(" ", r["keyword"], r["basicProfile"])
print("\n## Emptied by dicognito")
for r in rows:
    if outcome(r) == "emptied":
        print(" ", r["keyword"], r["basicProfile"])
print("\n## Changed, by VR")
print(Counter(r["vr"] for r in rows if outcome(r) == "changed"))
print("\n## Changed non-PN/UI/DA/DT/TM")
for r in rows:
    if outcome(r) == "changed" and r["vr"] not in ("PN", "UI", "DA", "DT", "TM"):
        print(" ", r["keyword"], r["vr"], r["basicProfile"], r["populated"])
print("\n## TM rows")
for r in rows:
    if r["vr"] == "TM":
        print(" ", r["keyword"], r["basicProfile"], outcome(r))
print("\n## UI rows unchanged")
for r in rows:
    if r["vr"] == "UI" and outcome(r) != "changed":
        print(" ", r["keyword"], r["basicProfile"], outcome(r))
