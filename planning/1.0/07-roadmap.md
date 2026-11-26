# Roadmap to dicognito 1.0

## What 1.0 should mean

| Quality | Concretely |
|---|---|
| **Stable** | A documented public API and CLI. A declared versioning scheme (Q10, [08-versioning.md](08-versioning.md)) with a written output-stability policy: which kinds of release may change which output, for the same input, seed and options. Deprecations announced one release before removal |
| **Safe** | No crash on malformed or empty input. Defaults that do not silently keep obviously identifying data (private attributes, overlay comments, AE titles, `RetrieveURL`, device serial numbers). Status attributes that do not over-claim. Clear statement of what is and is not covered |
| **Mature** | Behaviour described attribute by attribute, generated from the code. A conformance-style statement against PS3.15. CI that tests the installed command. Golden-output tests. "Development Status :: 5 - Production/Stable" |

## Decisions needed

These are the questions where the answer changes the plan. Recommendations are given; each is a decision for the maintainer.

| # | Decision | Options | Recommendation |
|---|---|---|---|
| Q1 | What is the default profile? | (a) today's behaviour, documented; (b) PS3.15 Basic Profile with conformant pseudonyms; (c) a named "dicognito" profile: Basic Profile plus options, with an explicit, short list of deviations | (c). Default = Basic + Retain Longitudinal (Modified Dates) + Retain Patient Characteristics + Retain Device Identity (with AE titles cleaned) + pseudonyms for D, and Clean Descriptors implemented by an echo scan (Q4) so `StudyDescription`, `SeriesDescription` and `ProtocolName` survive in cleaned form. Pseudonymizing `AccessionNumber`, `StudyID` and `PatientID` needs no deviation: Table E.1-1a lets Z and D attributes take a dummy value. Remaining deviations would be pseudonyms where the table says X (some IDs and addresses), which can be listed or removed. `--profile basic` gives strict Basic. Document the deviation list in the README. Do not set `PatientIdentityRemoved` or write PS3.15 codes when deviating |
| Q2 | Private attributes by default? | Keep (today), remove, remove with a safe-private allow-list | Remove by default; `--keep-private` for everything; `--keep-private-creator "SIEMENS CSA HEADER"` for an allow-list. Test-data users who need vendor tags opt in. This is the largest safety improvement available. *Added 2026-11-25:* if private elements are kept by default, write T-20 (explicit vs implicit VR give the same result, I-8), which needs a new fixture; if they are removed, T-20 is moot |
| Q3 | Dates: hours or days? | Keep the hour offset (fix orphan times by pairing better) or switch to whole days and leave times | Whole days (fixes I-3, I-4, I-5 at once). ✅ *Decided 2026-11-26: whole days, times of day unchanged. Recorded as ADR-0001 (`docs/adr/0001-whole-day-date-shift.md` on `main`, #209).* |
| Q4 | Descriptors under the default profile | Keep verbatim; remove; "clean" | Clean by echo detection: after anonymizing, search retained text attributes for the original values of names, IDs, dates and addresses dicognito replaced in that object (and tokens of them); replace any hit with the pseudonym or remove it; log it. This is cheap, deterministic, specific to dicognito's design (it knows the originals), and a defensible "C" for common leaks. It is not a guarantee and must be documented as heuristic |
| Q5 | Batch all output changes into one release? | Spread across releases; one batch | One batch (0.21), announced in advance, then the stability promise starts at 1.0. *Changed 2026-11-23: the batch is now part of 0.20 (Q11)* |
| Q6 | Hash construction | Keep MD5(seed + value); switch to HMAC-SHA-256(seed, value) | Switch in the output-change batch, if at all; it costs nothing extra then. Not needed for correctness |
| Q7 | Public API surface | Everything importable; minimal (`Anonymizer`, `ElementAnonymizer`, `ValueKeeper`, profile types) | Minimal. Rename internals with a leading underscore or move under `dicognito._internal`, keeping deprecated aliases for one minor release |
| Q8 | Pixel data in 1.0? | No; guard only; redaction | Guard only (see below) |
| Q9 | Mapping export (#124) | No; `--save-map` opt-in | Not for 1.0. Revisit with the ID lookup-table idea in 1.x; both need careful wording about the file being a re-identification key |
| Q10 | Versioning scheme | SemVer with a declared output contract; EffVer (Macro.Meso.Micro by upgrade effort) | EffVer, with an output-stability policy: linking values (identifiers, UIDs, patient names, dates) change only in macro releases; newly modified attributes ship as meso. See [08-versioning.md](08-versioning.md). ✅ **Decided 2026-11-23: EffVer, with the output-stability policy** |
| Q11 | `main` already changes every UID (#191). Release it soon, or hold it for the consistency batch? (added 2026-11-22) | (a) Release `main` as 0.20 after hardening, consistency batch as 0.21: incremental users re-anonymize twice. (b) Hold `main`'s next release until the consistency batch is in, and release both as 0.20: one re-anonymization. Meanwhile ship crash fixes (C-1, C-2, C-3), which change no output for valid input, as 0.19.x micro releases from `support/0.19` | (b). The release tooling now allows releases from `support/0.19` (#197), so holding `main` does not block crash fixes. The cost is that #187, #191, #192 and the Python 3.10 drop wait longer; if any of them is urgent, choose (a) and say so in the 0.20 notes. ✅ **Decided 2026-11-23: (b), hold `main` and release after the consistency batch.** Characterization tests first (T-0 completed, T-1, and as many others as is practical), then crash fixes, then the consistency batch, all on `main`, released together as 0.20.0. Incremental users re-anonymize once. 0.19.x releases from `support/0.19` only if someone needs a crash fix before then |
| Q12 | Does the patient's own name stay gendered? (added 2026-11-25) | (a) the patient's own names (`PatientName`, `OtherPatientNames`, `PatientBirthName`) take given names from the female or male list by the top-level `PatientSex`; every other PN uses one combined list regardless of context (fixes I-1 for other people); (b) every PN, the patient's included, uses the combined list | (a). A female patient with a male name looks wrong in a viewer, which matters to test-data users, and a patient's objects normally carry the same `PatientSex`. The cost: a patient whose objects disagree on `PatientSex` (or omit it in some) gets two pseudonyms. Must be decided before the I-1 fix. Decides T-9 |
| Q13 | Warn when re-anonymizing dicognito output? (added 2026-11-25) | (a) No, documented only (today, for `--in-place`); (b) warn when `DeidentificationMethod` contains `DICOGNITO`, and anonymize anyway; (c) skip such files; (d) refuse unless forced | (b), per I-17: re-running is sometimes deliberate (a second seed for another recipient), so skipping or refusing gets in the way. Decides T-30 |
| Q14 | `--output-directory` collisions: two objects get the same new SOP Instance UID (duplicates in the source, or `--keep SOPInstanceUID`) (added 2026-11-25) | (a) Overwrite silently (today); (b) treat the second as a failed file: do not write it, report it and exit non-zero, like other per-file failures (C-3); (c) write it under a modified name | (b). Losing an object silently is the worst outcome; (c) hides the duplicate and invents a file name. Decides T-31 |

## Release plan

Each bullet is intended as one small PR.

### 0.19.1: hotfix ✅ released 2026-11-21

Released from `support/0.19` (tag `0.19.1`), not from `main`.

- ✅ Restore `main(main_args=None)` (D-1): #195, issue #196.
- ✅ Release from a branch other than `main`: #197 (not in the original plan).
- ✅ *In part:* CI builds the wheel and runs `dicognito --version` from it (T-0). Still to do: run one anonymization through the installed command.
- ✅ Merge `support/0.19` into `main`: #203, merged 2026-11-23 (`main` at `dc343d4`).

### 0.19.x: crash fixes from `support/0.19`, only if needed (added 2026-11-22)

*Changed 2026-11-23 (Q11 decided as (b)):* not planned. The crash fixes are made on `main` and released in 0.20.0. Cut a 0.19.x micro release from `support/0.19` only if a user hits one of these crashes before 0.20 ships:

- Unparseable DA/DT/TM no longer raise (C-1).
- Empty components and `None` no longer raise (C-2), without changing what empty IDs become.
- CLI continues past failures and reports them (C-3).

### 0.20: characterize, harden and make consistent (one macro release)

*Changed 2026-11-22:* the original heading said "no intended output change for valid input". That no longer holds: `main` already carries output changes (conformant UIDs #191; `AdmissionID`, `ServiceEpisodeID`, `ReferringPhysicianAddress`, `ReferringPhysicianTelephoneNumbers` and `InstitutionAddress` without `InstitutionName` #192) and drops Python 3.10 (#185). Under Q10 this is already a macro release.

*Changed 2026-11-23 (Q11 decided as (b)):* `main` is not released until the consistency batch is in. The former 0.20 ("characterize and harden") and 0.21 ("consistency") stages are now one release, 0.20.0, the first under EffVer. Incremental users re-anonymize once for the UID and consistency changes together. Later stages are also expected to change linking values (for example patient names and institution names under the profile engine), so further re-anonymizations before 1.0 are expected and accepted (decided 2026-11-23); each such release is a macro release, announced in the release before it. The PRs keep their original order, so the safety net is in place before any behaviour changes.

#### Characterize (before any behaviour change)

1. ✅ Merge `support/0.19` into `main` (D-1 fix and release tooling): #203, merged 2026-11-23.
2. ✅ Complete T-0: run one anonymization through the installed command in the wheel smoke test. Issue #198. *#204, merged 2026-11-23.*
3. ✅ Golden-output test (T-1), with a script to regenerate the golden file. Issue #199. Generated from `main` *after* #191, so the UID change is not mistaken for a regression. *#205, merged 2026-11-23: `tests/test_seeded_output.py` against `tests/seeded_output.expected.json`, recording an action (changed, emptied, removed, added, kept) and value per element.*
4. ✅ Table E.1-1 coverage snapshot (T-2), with a script to regenerate it. The probe already exists. Issue #200. *#206, merged 2026-11-25: `tests/test_ps315_output.py` against `tests/ps315_output.expected.json`, recording action and exact value per attribute rather than only the outcome class. Neither test has a regenerate script: on a mismatch each writes a git-ignored `.actual.json` next to the expected file, to be compared and copied across (`how_to_build.md`).*
5. Known-defect `xfail` tests: the subset listed in [06-characterization-tests.md](06-characterization-tests.md#selection-before-behaviour-changes), as many as is practical. Issue #201.
6. Versioning policy (Q10): README section "Versioning and output stability" with the pinning guidance, and `micro`/`meso`/`macro` PR labels. Documentation only. Issue #202.

#### Harden (no output change for input that anonymized before)

- Unparseable DA/DT/TM no longer raise (C-1, T-5).
- Empty components and `None` no longer raise (C-2, T-3 in part), without yet changing what empty IDs become.
- CLI continues past failures and reports them (C-3, T-6).
- `--what-if` honours the other options (I-14, T-24).
- Reject over-long ID affixes (I-9, T-23).

#### Consistency (the output-change batch; formerly 0.21)

Each PR regenerates the golden file (T-1) and removes the `xfail` marker from its test.

- Empty in, empty out (I-6, #194).
- Person-name pseudonym independent of context (I-1). Needs Q12 decided first; that decision also decides T-9.
- Issuer pseudonymized consistently; issuer-related sequences handled (I-2).
- Whole-day date shift; times untouched; set `LongitudinalTemporalInformationModified` (I-3, I-4, I-5, I-15 part).
- Registry-UID rule (I-7). The PR also adds T-18 (a DICOMDIR anonymized with its instances still resolves), with the DICOMDIR fixture it needs.
- Name normalization (I-12, T-27), full `PatientAddress` (I-11), no added `InstitutionAddress` (I-13).
- Optional: HMAC-SHA-256 (Q6).

#### Release

- Release notes for 0.20.0 under an "Output changes" heading: UIDs (#191), the #192 attributes and every consistency change. State that the same seed gives different output than 0.19.x.
- After this release, the golden file changes only as the output-stability policy allows (Q10).

Done:

- ✅ Merge `fix/conformant-uis`: merged as #191 on 2026-11-21 and release-noted under Changed ("The same seed now produces different UIDs than in earlier versions").

### ~~0.21: consistency (the output-change batch)~~ (merged into 0.20 on 2026-11-23)

*Changed 2026-11-23 (Q11 decided as (b)):* this stage's items are now the "Consistency" part of 0.20 above. The version numbers of the later stages move down by one.

### 0.21: profile engine (formerly 0.22)

- `tools/generate_ps315_table.py`: reads NEMA's part15 DocBook XML, pinned to a recorded DICOM edition, writes `src/dicognito/_ps315_table.py` (a committed, generated module of `{tag: {column: action}}`, plus the repeating-group and private rules). Regenerating is a deliberate PR whose diff shows the standard's changes.
  - *Changed 2026-11-24:* NEMA's XML is the primary source, not innolitics. Innolitics' `standard/` folder was last regenerated at 2024b (commit `8670abd`, 2024-04-18); their update workflow was being fixed in April 2026 but nothing newer had been published by 2026-11-24, so a table built from it would start 1.0 more than two years behind. Use innolitics as a cross-check instead: the generator's output at 2024b should match their `confidentiality_profile_attributes.json` at `8670abd`.
  - The #200 test (`tests/test_ps315_output.py`) then takes its attribute list from the generated table, and `tests/ps315_table_2024b.json`, a one-off hand-made copy of the innolitics table with no refresh script, is deleted. The test and production then cannot drift onto different editions.
- An action model: `Remove`, `Empty`, `Keep`, `Dummy(generator)`, `NewUID`, `ShiftDate`, `Clean(cleaner)`; compound codes resolved by a fixed, documented rule.
- `Profile` = base table + options + overrides. Options mirror PS3.15 names. Dicognito's existing generators become the `Dummy` implementations for PN, IDs, addresses, institution; a generic VR-appropriate dummy for everything else.
- The VR-based handlers remain as a fallback for attributes outside the table (new or private-with-known-VR), so coverage never regresses.
- `--profile {dicognito,basic}` and `--option retain-device-identity`-style switches (exact CLI shape to decide; prefer one repeatable `--option` over many flags).
- `--what-if` prints the effective action per attribute, with the PS3.15 code, as a Markdown table; the README section "Exactly what does dicognito do?" is generated from it.
- Bite-sized order: generator script and table (no behaviour change, tested against T-2) → action model behind the existing handlers → switch one attribute group at a time (device identity, then contact and location, then identifiers, then descriptors) with T-2 diffs reviewed in each PR.

### 0.22: safety defaults and operations (formerly 0.23)

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
