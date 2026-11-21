# Dicognito 1.0 planning

Working documents for taking dicognito to a stable, safe, mature 1.0. They are meant to be iterated on; nothing here is a commitment yet.

Findings are based on branch `fix/conformant-uis` (`main` plus conformant `2.25.` UIDs) as of 2026-11-18, read from the source and confirmed with the probe scripts in [tools/](tools/).

## Documents

| Document | Contents |
|---|---|
| [01-background.md](01-background.md) | Mission, goals, non-goals, audiences, strengths, weaknesses, position relative to PS3.15, capability landscape of other tools, corrections to earlier external claims, draft public blurb |
| [02-behaviour-catalogue.md](02-behaviour-catalogue.md) | What dicognito does today, handler by handler, plus API and CLI |
| [03-ps315-gap-analysis.md](03-ps315-gap-analysis.md) | Every PS3.15 Table E.1-1 attribute probed against dicognito; grouped gaps |
| [04-inconsistencies.md](04-inconsistencies.md) | Defects, crashes, inconsistencies and surprises, with severities and proposed fixes |
| [05-empty-attributes.md](05-empty-attributes.md) | Empty-value behaviour and a proposed policy (extends issue #194) |
| [06-characterization-tests.md](06-characterization-tests.md) | Tests to add, and how each one changes when the related fix lands |
| [07-roadmap.md](07-roadmap.md) | Decisions needed, release-by-release plan, profile engine design, pixel-data position |
| [08-versioning.md](08-versioning.md) | SemVer versus EffVer for an anonymizer whose output is its contract; proposed output-stability policy, release-note and pinning guidance |
| [data/ps315-probe.csv](data/ps315-probe.csv) | Raw probe results, one row per Table E.1-1 attribute |

## Headline findings

1. 🔴 **The `dicognito` command is broken in the released 0.19.0.** It fails at start-up with `TypeError: main() missing 1 required positional argument`. Introduced by `9ffc4bb`; `python -m dicognito` still works. Needs a 0.19.1.
2. 🔴 **Crashes on real-world values** abort a whole command-line run: dates such as `00000000` or `20200230`, empty components in multi-valued dates and names, `None`-valued IDs.
3. 🔴 **Relationships break in two ways the tool exists to prevent:** a physician's pseudonym depends on the sex of the patient and on whether the name is inside a sequence; and patients with the same ID from different issuers merge, because every issuer becomes `DICOGNITO`.
4. 🟡 **Empty values become shared fake values** for IDs, so unrelated studies with no accession number end up sharing one.
5. 🟡 **Hour-based date shift** makes one source date map to two output dates, leaves times without a paired date unshifted, and defeats `--keep` on times. A whole-day shift fixes all three.
6. 🟡 **Coverage:** of 617 Table E.1-1 attributes, dicognito changes about 230 and never changes 274 (descriptions, comments, device identifiers, AE titles, patient characteristics, clinical-trial and specimen identifiers, contact details, GPS). Private attributes, overlays and curves are kept. UID coverage is nearly complete; 24 attributes holding registry UIDs are wrongly replaced.
7. Dicognito's pseudonyms are already conformant PS3.15 actions for D and Z attributes, and its date shift matches the Modified Dates option. That makes "PS3.15 profile with friendly options" a natural 1.0 architecture rather than a rewrite.

## Decisions needed first

Details and recommendations are in [07-roadmap.md](07-roadmap.md#decisions-needed). The ones that block planning:

- **Q1** Default profile: today's behaviour documented, strict Basic, or a named profile (Basic plus options plus a short deviation list). Recommended: the named profile.
- **Q2** Private attributes removed by default, with escape hatches. Recommended: yes.
- **Q3** Whole-day date shift. Recommended: yes.
- **Q5** Batch all seeded-output changes into one pre-1.0 release. Recommended: yes.
- **Q10** Versioning scheme. Recommended: EffVer with a written output-stability policy ([08-versioning.md](08-versioning.md)).

## Reproducing the probes

From the repository root, in the project environment:

```
uv run python planning/1.0/tools/probe_edges.py
uv run python planning/1.0/tools/probe_more.py
uv run python planning/1.0/tools/probe_table.py <confidentiality_profile_attributes.json> <out.csv>
uv run planning/1.0/tools/analyze_probe.py <out.csv>
```

The table JSON comes from `https://raw.githubusercontent.com/innolitics/dicom-standard/master/standard/confidentiality_profile_attributes.json`. The `planning` folder is excluded from ruff.
