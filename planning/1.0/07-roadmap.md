# Roadmap to dicognito 1.0

## What 1.0 should mean

| Quality | Concretely |
|---|---|
| **Stable** | A documented public API and CLI. Semantic versioning. A written output-stability promise: within a major version, the same input, seed and options produce the same output. Deprecations announced one minor release before removal |
| **Safe** | No crash on malformed or empty input. Defaults that do not silently keep obviously identifying data (private attributes, overlay comments, AE titles, `RetrieveURL`, device serial numbers). Status attributes that do not over-claim. Clear statement of what is and is not covered |
| **Mature** | Behaviour described attribute by attribute, generated from the code. A conformance-style statement against PS3.15. CI that tests the installed command. Golden-output tests. "Development Status :: 5 - Production/Stable" |

## Decisions needed

These are the questions where the answer changes the plan. Recommendations are given; each is a decision for the maintainer.

| # | Decision | Options | Recommendation |
|---|---|---|---|
| Q1 | What is the default profile? | (a) today's behaviour, documented; (b) PS3.15 Basic Profile with conformant pseudonyms; (c) a named "dicognito" profile: Basic Profile plus options, with an explicit, short list of deviations | (c). Default = Basic + Retain Longitudinal (Modified Dates) + Retain Patient Characteristics + Retain Device Identity (with AE titles cleaned) + pseudonyms for D, and Clean Descriptors implemented by an echo scan (Q4) so `StudyDescription`, `SeriesDescription` and `ProtocolName` survive in cleaned form. Pseudonymizing `AccessionNumber`, `StudyID` and `PatientID` needs no deviation: Table E.1-1a lets Z and D attributes take a dummy value. Remaining deviations would be pseudonyms where the table says X (some IDs and addresses), which can be listed or removed. `--profile basic` gives strict Basic. Document the deviation list in the README. Do not set `PatientIdentityRemoved` or write PS3.15 codes when deviating |
| Q2 | Private attributes by default? | Keep (today), remove, remove with a safe-private allow-list | Remove by default; `--keep-private` for everything; `--keep-private-creator "SIEMENS CSA HEADER"` for an allow-list. Test-data users who need vendor tags opt in. This is the largest safety improvement available |
| Q3 | Dates: hours or days? | Keep the hour offset (fix orphan times by pairing better) or switch to whole days and leave times | Whole days (fixes I-3, I-4, I-5 at once) |
| Q4 | Descriptors under the default profile | Keep verbatim; remove; "clean" | Clean by echo detection: after anonymizing, search retained text attributes for the original values of names, IDs, dates and addresses dicognito replaced in that object (and tokens of them); replace any hit with the pseudonym or remove it; log it. This is cheap, deterministic, specific to dicognito's design (it knows the originals), and a defensible "C" for common leaks. It is not a guarantee and must be documented as heuristic |
| Q5 | Batch all output changes into one release? | Spread across releases; one batch | One batch (0.21), announced in advance, then the stability promise starts at 1.0 |
| Q6 | Hash construction | Keep MD5(seed + value); switch to HMAC-SHA-256(seed, value) | Switch in the output-change batch, if at all; it costs nothing extra then. Not needed for correctness |
| Q7 | Public API surface | Everything importable; minimal (`Anonymizer`, `ElementAnonymizer`, `ValueKeeper`, profile types) | Minimal. Rename internals with a leading underscore or move under `dicognito._internal`, keeping deprecated aliases for one minor release |
| Q8 | Pixel data in 1.0? | No; guard only; redaction | Guard only (see below) |
| Q9 | Mapping export (#124) | No; `--save-map` opt-in | Not for 1.0. Revisit with the ID lookup-table idea in 1.x; both need careful wording about the file being a re-identification key |

## Release plan

Each bullet is intended as one small PR.

### 0.19.1: hotfix

- Restore `main(main_args=None)` (D-1).
- CI: build the wheel, install it, run `dicognito --version` and one anonymization (T-0).

### 0.20: characterize and harden (no intended output change for valid input)

- Golden-output test (T-1) and Table E.1-1 coverage snapshot (T-2), with a script to regenerate them.
- Commit the `xfail` tests for known defects (06-characterization-tests.md).
- Unparseable DA/DT/TM no longer raise (C-1).
- Empty components and `None` no longer raise (C-2) without yet changing what empty IDs become.
- CLI continues past failures and reports them (C-3).
- `--what-if` honours the other options (I-14).
- Reject over-long ID affixes (I-9).
- Merge `fix/conformant-uis` (UID output change already in flight; release-note it).

### 0.21: consistency (the output-change batch)

Announce in 0.20's release notes that 0.21 changes seeded output.

- Empty in, empty out (I-6, #194).
- Person-name pseudonym independent of context (I-1).
- Issuer pseudonymized consistently; issuer-related sequences handled (I-2).
- Whole-day date shift; times untouched; set `LongitudinalTemporalInformationModified` (I-3, I-4, I-5, I-15 part).
- Registry-UID rule (I-7).
- Name normalization (I-12), full `PatientAddress` (I-11), no added `InstitutionAddress` (I-13).
- Optional: HMAC-SHA-256 (Q6).
- After this release, the golden file is frozen until 2.0.

### 0.22: profile engine

- `tools/generate_ps315_table.py`: reads the innolitics JSON (or NEMA's part15 DocBook XML), pinned to a recorded DICOM edition, writes `src/dicognito/_ps315_table.py` (a committed, generated module of `{tag: {column: action}}`, plus the repeating-group and private rules). Regenerating is a deliberate PR whose diff shows the standard's changes.
- An action model: `Remove`, `Empty`, `Keep`, `Dummy(generator)`, `NewUID`, `ShiftDate`, `Clean(cleaner)`; compound codes resolved by a fixed, documented rule.
- `Profile` = base table + options + overrides. Options mirror PS3.15 names. Dicognito's existing generators become the `Dummy` implementations for PN, IDs, addresses, institution; a generic VR-appropriate dummy for everything else.
- The VR-based handlers remain as a fallback for attributes outside the table (new or private-with-known-VR), so coverage never regresses.
- `--profile {dicognito,basic}` and `--option retain-device-identity`-style switches (exact CLI shape to decide; prefer one repeatable `--option` over many flags).
- `--what-if` prints the effective action per attribute, with the PS3.15 code, as a Markdown table; the README section "Exactly what does dicognito do?" is generated from it.
- Bite-sized order: generator script and table (no behaviour change, tested against T-2) → action model behind the existing handlers → switch one attribute group at a time (device identity, then contact and location, then identifiers, then descriptors) with T-2 diffs reviewed in each PR.

### 0.23: safety defaults and operations

- Private attributes removed by default, with escape hatches (Q2).
- Overlay comments and curve data removed; overlay bitmap data: follow the chosen profile (Basic removes it; a `--keep-overlays` escape hatch for viewer testing).
- AE titles and `RetrieveURL`/`RetrieveURI` handled (pseudonymize AE titles consistently, so routing tests still see distinct, stable AEs).
- Echo detection (Q4) over retained text, with a log line per hit.
- `--report report.json`: per-run summary of actions taken (counts by attribute and action, files failed, echo hits). No original values in the report.
- Require `-o` or `-i` (promised in 0.15.0).
- Widen the burned-in annotation guard (see pixel data).

### 1.0.0rc1 → 1.0.0

- API cut (Q7), deprecated aliases removed.
- Documentation: README rewritten around the blurb in [01-background.md](01-background.md); a "conformance statement" page listing the default profile, options, deviations and the date-modification method (PS3.15 E.3.6 asks for this); a page for test-data recipes (`--seed` loops for load tests, `--id-prefix` for labelling); an extension guide for handlers and profiles.
- Classifier "Production/Stable"; release notes collect every Changed item since 0.19.
- A release candidate exercised on real Enterprise Imaging test data before final.

## After 1.0 (1.x candidates)

- Config file (TOML) for overrides and profiles, so a team can check in its settings.
- ID lookup table (`--map ids.csv`) for assigned identifiers (trial subject IDs).
- Per-patient date offsets as an option.
- `--skip`/`--quarantine-dir` filters on header conditions.
- Mapping export (#124), opt-in, documented as a re-identification key.
- Parallel processing for large trees.
- Optional pixel redaction (below).

## Pixel data

**Argument for doing it.** Ultrasound, secondary capture, screen captures, dose reports and some scanned documents have patient names and dates burned into the pixels. Header-only anonymization of those objects is not anonymization. Test-data builders do want those modalities (they exercise different viewer and PACS paths), and today they must redact by hand or exclude them.

**Argument against doing it now.** Doing it well needs pixel decoding for compressed transfer syntaxes (numpy plus pylibjpeg/OpenJPEG/GDCM plugins: a large dependency jump from "pydicom only"), re-encoding decisions (lossy re-compression changes images; writing uncompressed changes transfer syntax and size), per-manufacturer region rules that must be maintained, multi-frame and color handling, and validation. OCR-based detection adds heavier dependencies and false negatives. A partial feature invites false confidence, and dicognito's distinctive value is in the header.

**Recommendation.** Not in 1.0. In 1.0, make the boundary explicit and safer:

1. Extend `BurnedInAnnotationGuard` with header heuristics for "likely burned in" even when `BurnedInAnnotation` is absent: modality `US`, `XC`, `OT`, `SM`; secondary-capture and dose-report-image SOP classes; `ImageType` containing `SECONDARY` or `SCREEN SHOT`; `ConversionType` present. Default action stays `warn`, and the summary counts these objects.
2. Document the boundary in the README's first screen.

**Plan if pursued in 1.x** (as an optional extra, `pip install dicognito[pixels]`):

1. Rule file of rectangles keyed by header conditions (manufacturer, model, rows, columns, SOP class), in a simple documented format; consider reading an existing community format rather than inventing one.
2. Decode with pydicom's pixel handlers; black out rectangles; write uncompressed Explicit VR Little Endian (never re-encode lossy); update `BurnedInAnnotation = NO` only when a rule matched and was applied; record the action in `DeidentificationMethod`.
3. Objects with likely burned-in text and no matching rule: warn, or quarantine with `--on-burned-in-annotation quarantine`.
4. No OCR in dicognito itself.
