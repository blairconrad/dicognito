# Handling of empty attributes

Builds on [issue #194](https://github.com/blairconrad/dicognito/issues/194), which proposes "leave an empty value empty across all handlers". This document adds probe evidence, the cases #194 does not cover, and answers to its open questions.

## Kinds of "empty"

| Kind | Example | How pydicom presents it |
|---|---|---|
| Absent | no `AccessionNumber` element | `"AccessionNumber" not in ds` |
| Present, zero length (text VR) | Type 2 `AccessionNumber` sent empty | `""` by default; `None` if `pydicom.config.use_none_as_empty_text_VR_value` is set |
| Present, zero length (other VR) | empty `PatientWeight`, empty `OB` | `None` / `b""` |
| Present, empty sequence | `ReferencedStudySequence` with no items | `Sequence([])` |
| Multi-valued with an empty component | `OtherPatientIDs = "A1\"` | `["A1", ""]` |
| Whitespace only | `"  "` | Usually stripped to `""` by pydicom for text VRs |

## Current behaviour (probed)

| Handler | Absent | Zero-length `""` | `None` | Empty component in multi-value |
|---|---|---|---|---|
| Stripper (11 attributes) | absent | removed | removed | removed |
| UI | absent | `""` | `None` | (code reading) replaced, `""` hashed to a UID |
| PN | absent | `""` | `None` | **crash** (`TypeError`) |
| ID (16 attributes) | absent | **generated ID, the same for every empty value** | **crash** (`TypeError`) | **generated ID** |
| `IssuerOfPatientID` | absent | `""` | `None` | (code reading) whole value becomes `DICOGNITO` |
| Address (4 attributes) | absent | `""` | `None` | n/a (VM 1) |
| `InstitutionName` | absent | **generated clinic name, and generated `InstitutionAddress` is set (added if absent)** | (code reading) crash in the randomizer | n/a |
| `InstitutionAddress` | absent | `""` | `None` | n/a |
| `InstitutionalDepartmentName` | absent | **`RADIOLOGY`** | **`RADIOLOGY`** | n/a |
| Fixed value (2 attributes) | absent | `""` | `""` | `""` |
| DA/DT | absent | `""` | `None` | **crash** (`ValueError`) |
| TM (paired) | absent | `""` (and its date is shifted as date-only) | same | (code reading) components padded by `zip_longest` |
| Everything else | absent | unchanged | unchanged | unchanged |
| Sequences | absent | kept, empty | n/a | n/a |

Dataset-level: `DeidentificationMethod` is always added; `PatientIdentityRemoved` may be added. No other attribute is ever added except `InstitutionAddress` (above).

## Why "empty in, empty out" is right

1. **Empty means unknown.** A Type 2 attribute sent empty says the value is not known. Filling it invents information.
2. **Filling creates false relationships.** All empty values hash to the same pseudonym for a seed. Every study that had no accession number now shares one accession number (`VENLPRZ6TMV1` in the probe); every object with an empty `PatientID` belongs to the same patient. For a PACS, that merges unrelated studies and patients, which is the exact opposite of dicognito's goal of preserving relationships.
3. **It is what the standard does.** PS3.15's Z action is "replace with a zero-length value"; an already-empty value satisfies Z, and also satisfies D for Type 2 attributes.
4. **It keeps files valid.** Type 2 attributes stay present; Type 1 attributes that arrive empty were already invalid, and dicognito should not hide that.
5. **It is predictable.** One rule instead of per-handler exceptions; easy to test generically.

## Answers to #194's open questions

**Should identifiers also stay empty, or keep generating values so records stay linkable?** Stay empty. Generated values do not make records linkable in any meaningful way; they make unrelated records falsely linked. Records that are genuinely related are already linked by their non-empty identifiers and UIDs.

**Should tests assert empty-stays-empty for every handler, or only the changed ones?** Every handler, through one parametrized test over a representative attribute per handler (and over every attribute in the ID list), for each kind of empty in the table above. The handlers that already behave are exactly the ones a refactoring towards a profile engine could break.

## Proposed policy

1. An absent attribute is never added, except the de-identification status attributes (`DeidentificationMethod`, `PatientIdentityRemoved` when warranted, `LongitudinalTemporalInformationModified` when dates are shifted, `DeidentificationMethodCodeSequence` if adopted).
2. A present attribute with a zero-length value (`""`, `None`, `b""`, empty sequence) stays present with the same empty value, unless the action is remove (X), in which case it is removed.
3. In a multi-valued attribute, each empty component stays empty and the others are processed; the number of values is preserved.
4. Empty never raises.
5. For `InstitutionName`/`InstitutionAddress`: an empty name is treated as missing in both handlers, so a non-empty address is anonymized on its own.
6. Whitespace-only values are treated as empty.

## Consequences

- **Output change** for empty `PatientID`, `AccessionNumber`, `StudyID`, `StationName`, `AdmissionID`, other IDs, `InstitutionName`, `InstitutionalDepartmentName`. Release-note it under Changed.
- Fixes three crashes (PN component, `None` ID, DA component).
- Escape hatch if someone needs populated values for testing (a PACS that rejects empty accession numbers): YAGNI for now. If requested, a per-attribute fill option that generates a *distinct* value per object (seeded by the SOP Instance UID or Study Instance UID, not by the empty string) would avoid false merging.

## Characterization tests to write first

Write these against current behaviour before changing anything (they are listed with the others in [06-characterization-tests.md](06-characterization-tests.md)). Each test that asserts "becomes populated" flips when the policy lands; each test that asserts "stays empty" already passes and guards the policy. Each crash test asserts the exception today, marked `xfail(strict=True)` with the post-fix expectation, so it starts passing (and fails `xfail_strict`) when fixed.
