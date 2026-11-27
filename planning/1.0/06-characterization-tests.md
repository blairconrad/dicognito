# Characterization tests to add

The existing suite (341 tests, all passing) covers each handler's happy path, multi-object relationship cases (one series, one study, one patient, two patients), seed reproducibility within one version, ID affixes, the command line, and README/`--what-if` agreement. It mostly asserts "changed" or "not changed", rarely exact values.

What it does not pin down: exact output for a seed (so an accidental output change goes unnoticed), coverage across the standard's attribute list, empty values, malformed values, context dependence, private and SR content, and the installed console command.

## Conventions

- **Behaviour to keep:** a plain test asserting current behaviour.
- **Known defect:** a test asserting the *desired* behaviour, marked `@pytest.mark.xfail(strict=True, reason="<item id> <short reason>")`. The project sets `xfail_strict = true`, so the test fails the build the moment the defect is fixed, which forces removing the marker in the fixing PR. This avoids characterization tests that assert a wrong value and would have to be rewritten.
- **Output to freeze:** golden files (see T-1, T-2), changed only deliberately, so output changes show up as reviewable diffs. *As built:* on a mismatch the test writes a git-ignored `.actual.json` beside the `.expected.json`, and the intended changes are copied across by hand (`how_to_build.md`).
- A characterization test that asserts empty, absent or `None` must give a different result once the related fix lands. Each such test below says how it would change.

## Proposed tests

| ID | Test | Asserts today | After the planned fix | Relates to |
|---|---|---|---|---|
| T-0 | `test_console_script_runs`: build the wheel, install it in a temporary environment, run `dicognito --version` | `xfail` on 0.19.0 code (exit status ≠ 0) | Passes | D-1. ✅ *Done in part in 0.19.1 (#195): CI "Smoke test wheel" step runs `dicognito --version` from the wheel, plus a unit test on the `main` signature. Remaining: one anonymization through the installed command, and the change reaching `main`* ✅ *Completed: #203 brought it to `main`; #204 (2026-11-23) runs one anonymization through the installed command* |
| T-1 | Golden output: anonymize a rich fixture (the `load_test_instance` dataset plus SR, private and multi-valued elements) with seed `"golden"`; compare every element to a committed JSON file | Current exact output | Regenerated in the one release that batches output changes; then frozen for 1.x | 1.0 stability promise. ✅ *Done in #205 (2026-11-23): `tests/test_seeded_output.py` against `tests/seeded_output.expected.json`, recording an action (changed, emptied, removed, added, kept) and value per element* |
| T-2 | Table E.1-1 coverage snapshot: for each attribute in the generated PS3.15 table, the outcome class (removed / emptied / changed / unchanged / sequence-walked) for populated and empty values, compared to a committed CSV (the probe in [tools/probe_table.py](tools/probe_table.py) turned into a test) | Today's 617-row outcome | Updated by every coverage PR; the diff shows exactly which attributes changed | Gap analysis. ✅ *Done in #206 (2026-11-25): `tests/test_ps315_output.py` against `tests/ps315_output.expected.json`, recording action and exact value per attribute instead of an outcome class, from a pinned 2024b table until the generated table exists* |
| T-3 | Empty values, parametrized over one attribute per handler and every ID attribute, for `""`, `None`, `b""`, empty sequence, empty component | `""` stays `""` for PN, UI, DA, DT, addresses, issuer, fixed values (plain tests); IDs, `InstitutionName`, `InstitutionalDepartmentName` become populated (`xfail` desired "stays empty"); `None` ID, PN component, DA component crash (`xfail` desired "stays empty, no exception") | All plain | I-6, C-2, #194 |
| T-4 | Two empty `AccessionNumber` values in two objects stay distinct from each other (both empty) | `xfail` (both become `VENLPRZ6TMV1`) | Passes | I-6 |
| T-5 | Unparseable dates: `UNKNOWN`, `00000000`, `20200230`, `20200102-20200105`, `["20200102", ""]` do not raise, and the original value is not retained | `xfail` (raise) | Passes | C-1 |
| T-6 | CLI continues past a bad file, reports it, exits non-zero, and writes every good file | `xfail` (aborts) | Passes | C-3 |
| T-7 | Same `ReferringPhysicianName` in a female patient's object, a male patient's object and an object without `PatientSex` gives one pseudonym | `xfail` | Passes | I-1. ✅ *Done in #208, tidied in #210.* |
| T-8 | Same `PerformingPhysicianName` at top level and inside a sequence item gives one pseudonym | `xfail` | Passes | I-1. ✅ *Done in #208, tidied in #210.* |
| T-9 | `PatientName` of a female patient still gets a female given name (keep gendering for the patient's own name, if that is the decision) | Passes | Passes | I-1 |
| T-10 | Same `PatientID` with two different `IssuerOfPatientID` values gives two different (ID, issuer) pairs | `xfail` | Passes | I-2. ✅ *Done in #208, tidied in #210.* |
| T-11 | Same `PatientID` and issuer across objects gives the same (ID, issuer) pair | Passes | Passes | I-2. ✅ *Done in #208, tidied in #210.* |
| T-12 | `StudyDate` with `StudyTime` and `SeriesDate` without a time, same original date, shift to the same date | `xfail` | Passes | I-3. ✅ *Done in #208, tidied in #210.* |
| T-13 | Date shifts are whole days for many seeds (`(original − new).seconds == 0`) | `xfail` | Passes | I-3. ✅ *Done in #208, tidied in #210.* |
| T-14 | A time without a date (`SeriesTime` alone) is unchanged | Passes | Passes | I-4. *Changed 2026-11-26: the original assertion, that unpaired and paired times keep their difference, is moot once dates shift by whole days and times are left alone (ADR-0001); it duplicated T-13 and T-15, and its `SeriesTime` half passes today, so it became a plain test.* ✅ *Done in #208, tidied in #210.* |
| T-15 | `--keep StudyTime` keeps `StudyTime` | `xfail` | Passes | I-5. ✅ *Done in #208, tidied in #210.* |
| T-16 | Registry UIDs in non-class attributes are kept (`CodingSchemeUID = 1.2.840.10008.2.16.4`, `ReferencedTransferSyntaxUIDInFile`, `ReferencedSOPClassUIDInFile`) | `xfail` | Passes | I-7 |
| T-17 | `ManufacturerDeviceClassUID` with a non-registry value is replaced | `xfail` | Passes | I-7 |
| T-18 | A DICOMDIR anonymized with the instances it references still resolves each `ReferencedSOPInstanceUIDInFile` to an anonymized instance, and keeps `ReferencedSOPClassUIDInFile` | `xfail` (class UID replaced) | Passes | I-7 |
| T-19 | Cross-object references: `ReferencedSOPInstanceUID` in a presentation state or SR equals the anonymized `SOPInstanceUID` of the referenced image anonymized in the same run, including when the referencing object is processed first | Passes | Passes | Goal 1 |
| T-20 | Private PN/UI/DA elements: explicit-VR file vs the same dataset written implicit VR give the same result | `xfail` | Passes (or moot once private elements are removed by default) | I-8 |
| T-21 | SR content items: PNAME, UIDREF, DATE, DATETIME changed; TEXT and TIME kept (characterize) | Plain. Verify the TIME expectation when the test is written | Plain | I-4. *Changed 2026-11-26: the TIME `xfail` assumed times shift with their dates; under ADR-0001 times of day are left alone, so TIME is kept and the test is plain* |
| T-22 | Overlay comments (60xx,4000) and curve data (50xx) are kept | Plain (characterize) | Changes when Clean Graphics or default removal lands | Gap analysis |
| T-23 | ID affixes that leave fewer than 6 random characters are rejected (`ValueError`, CLI usage error) | `xfail` | Passes | I-9 |
| T-24 | `--what-if --keep PatientName` lists "Keep PatientName values" | `xfail` | Passes | I-14 |
| T-25 | `InstitutionName` only: `InstitutionAddress` not added | `xfail` | Passes | I-13 |
| T-26 | `PatientAddress` gets a full address, like `ReferringPhysicianAddress` | `xfail` | Passes | I-11 |
| T-27 | Name variants `DOE^JOHN`, `doe^john`, `DOE^JOHN ` give one pseudonym | `xfail` | Passes | I-12 |
| T-28 | `LongitudinalTemporalInformationModified` is `MODIFIED` when dates were shifted | `xfail` | Passes | I-15 |
| T-29 | Partial and zoned DT values keep precision and suffix (`2020` → 4 characters; `…+0500` keeps `+0500`) | Plain (exists partly) | Plain | |
| T-30 | Re-anonymizing output warns | `xfail` | Passes, if decided | I-17 |
| T-31 | `--output-directory` with two objects that get the same new SOP Instance UID does not silently overwrite | `xfail` | Passes, if decided | Smaller observations |

## Order

1. T-0 with the 0.19.1 hotfix. ✅ *Done in part in 0.19.1, completed in #204.*
2. T-1 and T-2 before any behaviour change, so every later PR shows its effect as a diff. ✅ *T-1 in #205, T-2 in #206; T-0 completed in #204.*
3. T-3 to T-6 (empties and crashes) together with their fixes, since those fixes are safe.
4. The remaining `xfail` tests in one PR, so the list of known defects is visible in the suite, then removed one fix at a time.

*Changed 2026-11-23:* roadmap Q11 was decided as "hold `main` until the consistency batch is in, with T-0, T-1 and as many other characterization tests as is practical first". All of this happens before 0.20.0. In step 3, each test lands first as `xfail` and its fix follows in a separate PR, so the test is seen to fail before the fix.

## Selection before behaviour changes

Decided 2026-11-23. "Required" must be in before the first behaviour-changing PR; "practical" means the test needs only small in-memory datasets or existing fixtures, so it goes in if ready; "later" needs a fixture or a decision that does not exist yet.

| Group | Tests | Status |
|---|---|---|
| Smoke and golden output | T-0 (complete it), T-1 | Required. ✅ Done (#204, #205) |
| Coverage snapshot | T-2 | Practical: the probe exists and becomes the test. ✅ Done (#206) |
| Crashes and empties, as `xfail` | T-3, T-4, T-5, T-6 | Practical |
| Relationships and dates, as `xfail` or plain | T-7, T-8, T-10, T-11, T-12, T-13, T-14, T-15 | Practical. ✅ Done (#208, #210; T-9 waits for Q12) |
| UID rules, as `xfail` or plain | T-16, T-17, T-19 | Practical |
| Remaining behaviour, as `xfail` or plain | T-21, T-22, T-23, T-24, T-25, T-26, T-27, T-28, T-29 | Practical |
| Needs a new fixture | T-18 (DICOMDIR with referenced instances), T-20 (same dataset written explicit and implicit VR) | Later: T-18 lands with the registry-UID fix (I-7); T-20 only if Q2 keeps private elements |
| Needs a decision first | T-9 (Q12), T-30 (Q13), T-31 (Q14) | Later: these assert behaviour that has not been decided, so an `xfail` would encode a guess. Each is written when its question is decided |

*Changed 2026-11-25:* T-27 moved from "needs a decision" to "practical": the roadmap's consistency batch already includes name normalization (I-12). The deferred tests now each have an owner in [07-roadmap.md](07-roadmap.md): a Q entry or the PR that needs them.
