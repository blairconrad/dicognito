# Inconsistencies, defects and surprises

Each item states current behaviour (with the evidence), why it matters, and a proposed resolution. Severity: 🔴 must fix before 1.0 · 🟡 should fix before 1.0 · 🟢 suggestion · 💭 question. Items marked **output change** alter what an existing seed produces, which matters for anyone relying on seeds for reproducibility; batch them into one release before 1.0.

Probe scripts: [tools/probe_edges.py](tools/probe_edges.py) (items not otherwise attributed).

## Release defect

### ✅ D-1 The `dicognito` command is broken in 0.19.0

**Status 2026-11-22: released fix, not yet on `main`.** 0.19.1 (tag `0.19.1`, branch `support/0.19`, on PyPI) restores `main(main_args: Sequence[str] | None = None)`, adds a unit test that the parameter defaults to `None`, and adds a CI step that runs `dicognito --version` from the built wheel (#195, issue #196). `main` at `b9b77ac` still has the defect; merge `support/0.19` into `main` before the next release from `main`. *2026-11-23: merged by #203; fixed on `main`.*

`uvx --from dicognito==0.19.0 dicognito --version` fails with `TypeError: main() missing 1 required positional argument: 'main_args'`; 0.18.0 works. Commit `9ffc4bb` removed the default from `main(main_args=None)`; the console-script entry point calls `main()` with no arguments. `python -m dicognito` still works. Tests call `main(args)` directly, and the `smoketest` folder present in 0.18.0 no longer exists.

Resolution: restore `main(main_args: Sequence[str] | None = None)`; add a test that invokes the installed entry point (for example `subprocess.run(["dicognito", "--version"])` in CI after installing the built wheel); release 0.19.1 promptly.

## Crashes on real-world input

### 🔴 C-1 Malformed dates abort the run

`StudyDate` values `UNKNOWN`, `00000000`, `20200230`, a range (`20200102-20200105`) and a multi-valued date with an empty component all raise `ValueError` in `DateTimeAnonymizer._shift_datetime`. The CLI then exits with status 1 part-way through a tree. `00000000` and impossible dates do occur in data from real modalities.

Resolution: never raise on a value dicognito cannot parse. Choose one policy for unparseable DA/DT/TM: replace with an empty value (safe, Type 2-friendly) or remove; log a warning naming the file and tag. Keeping the original value is not acceptable, because it may be a real date with odd punctuation.

### 🔴 C-2 Empty components of multi-valued PN, and `None` IDs, crash

- `OtherPatientNames = ["", "DOE^JANE"]` raises `TypeError: can only concatenate str (not "PersonName") to str`, because `_new_pn` only converts truthy values to `str`. (Probe: `probe_more.py`.)
- A zero-length ID whose value is `None` (pydicom's representation when `config.use_none_as_empty_text_VR_value` is set, or when created programmatically) raises `TypeError` in `Randomizer.to_int`.

Resolution: part of the empty-value policy ([05-empty-attributes.md](05-empty-attributes.md)): empty components stay empty, `None` is treated as empty.

### 🟡 C-3 One bad file aborts the whole command-line run

Any exception logs the file name and exits with status 1. With `--in-place`, earlier files are already overwritten and later files are untouched, so a partly anonymized tree is left behind.

Resolution: process every file, log failures, print a failure count, exit non-zero if any failed. Optionally `--fail-fast` for the old behaviour. For `--output-directory`, nothing for a failed file should be written.

## Relationship and consistency defects

### 🔴 I-1 The same person gets different pseudonyms depending on context (**output change**)

`PNAnonymizer` picks first names from the female or male list according to `PatientSex` in the dataset that contains the element. So:

| Original | Context | Pseudonym |
|---|---|---|
| `WELBY^MARCUS` as `ReferringPhysicianName` | female patient | `PORTER^SONDRA^LUCINDA` |
| same | male patient | `PORTER^LOYD^LUCINDA` |
| same | no `PatientSex` | `PORTER^LOYD^IAN` |
| `HOUSE^GREGORY` as `PerformingPhysicianName` | top level of a female patient's object | `LARSON^SELMA^EDDY` |
| same | inside a sequence item of the same object | `LARSON^DANTE^EUGENIO` |

A referring physician or operator who sees both male and female patients becomes several people, which breaks "studies by referring physician" tests and worklist filtering. The patient's own name also depends on whether `PatientSex` is present and where.

Resolution: gender only the patient's own names (`PatientName`, `OtherPatientNames`, `PatientBirthName`), using the top-level `PatientSex`; use the combined list for every other PN. Alternative: drop gendering entirely. Either way, make the choice of first-name list a function of the original value and the attribute, never of the surrounding dataset. *The choice is tracked as Q12 (2026-11-25).*

### 🔴 I-2 Distinct patients with the same ID from different issuers merge (**output change**)

Two patients, `PatientID = 123` with `IssuerOfPatientID = HOSP_A` and `PatientID = 123` with `HOSP_B`, both become `PatientID = P9TKK8ZFR289`, `IssuerOfPatientID = DICOGNITO`, with different names. A PACS that keys on ID plus issuer now sees one patient with conflicting demographics. Multi-issuer data is exactly what cross-enterprise (IHE PIX/XDS-I) test data needs. (Probe: `probe_more.py`.)

Resolution: pseudonymize `IssuerOfPatientID` consistently (an ID-style or organisation-style value derived from the original issuer) instead of a constant. Also handle `IssuerOfPatientIDQualifiersSequence` (`UniversalEntityID` and related), `IssuerOfAdmissionID`, `IssuerOfServiceEpisodeID`, `IssuerOfAccessionNumberSequence` content, and the order-number issuers in the same way. Keeping a constant issuer while the IDs collide is the worst combination.

### 🟡 I-3 Date shift depends on whether a time is present (**output change**)

The offset is a whole number of hours. A date with a time is shifted as an instant; a date without one is shifted as if it were midnight. With the probe seed:

| Original | Result |
|---|---|
| `StudyDate 20200102`, `StudyTime 230000` | `20180314 170000` |
| `SeriesDate 20200102` (no time) | `20180313` |
| `ContentDate 20200102`, `ContentTime 010000` | `20180313 190000` |
| SR `DATE` item `20200102` vs `DATETIME` item `20200102101010` | `20180313` vs `20180314041010` |

So one calendar day in the source becomes two days in the output, study and series dates disagree, and the day-interval between two dates can change by one depending on times.

### 🟡 I-4 Times without a paired date are not shifted

`SeriesTime` without `SeriesDate`, `AcquisitionTime` without `AcquisitionDate`, SR `TIME` content items, and every TM whose date partner is absent or named irregularly are kept while their siblings are shifted by up to 23 hours. In the probe, `StudyTime 100000 → 040000` while `SeriesTime 100200` and `AcquisitionTime 100500` stayed, so the series appears to start six hours after the study.

*Added 2026-11-23:* the partner time is found by guessing its keyword, `data_element.keyword.replace("Date", "Time")` (`datetimeanonymizer.py`, `_anonymize_date_and_time`), then testing `time_name in dataset`. When the guessed keyword is not in the DICOM dictionary (for example `LastMenstrualTime`, `EthicsCommitteeApprovalEffectivenessStartTime`), the test returns False but pydicom 3 emits `UserWarning: Invalid value '<keyword>' used with the 'in' operator`. The PS3.15 expected-output test (#200) triggers 10 such warnings; real files with those dates do the same on the command line. No output change. If the whole-day shift below is adopted (Q3), the partner-time lookup is removed and the warning goes with it; if not, check the guessed keyword against pydicom's dictionary before the `in` test, as a micro fix in the 0.20 hardening list.

### 🟡 I-5 `--keep` on a time does not keep it

`--keep StudyTime` keeps nothing: the `StudyDate` handler rewrites `StudyTime`. (`--keep StudyDate` keeps both, which is tested.)

**Proposed resolution for I-3, I-4 and I-5 together:** make the offset a whole number of days and stop changing TM values. Dates then shift identically with or without times, every time stays consistent with every other, `--keep` works per attribute, and DT values keep their time of day. Cost: times of day are retained. PS3.15 2026d E.3.6 (Retain Longitudinal Temporal Information with Modified Dates) asks for a modification that "aggregates or transforms dates so as to reduce the possibility of matching for re-identification", "preserves the gross longitudinal temporal relationships" and "preserves the fine temporal relationships between images and real-world events", adds `LongitudinalTemporalInformationModified = MODIFIED`, and requires the conformance statement to describe the method. A whole-day shift meets all three criteria. Table E.1-1 marks TM attributes `C` under this option too, so leaving times unchanged is a judgment that time of day alone is not identifying; it should be documented as such. This is an output change for every dated object, so it belongs in the same batch as I-1 and I-2.

### 🟡 I-6 Empty values: "empty in, empty out" for most handlers but not IDs or institution

See [05-empty-attributes.md](05-empty-attributes.md) and issue #194. The sharpest consequence: every empty `AccessionNumber` (and `PatientID`, `StudyID`, …) maps to the same generated value for a seed (`VENLPRZ6TMV1` in the probe), so unrelated records that lacked an accession number now share one.

### 🟡 I-7 Registry UIDs are replaced; one instance-like class UID is kept

The "keyword ends in `ClassUID`, or is `TransferSyntaxUID`" rule replaces 24 dictionary attributes that hold well-known UIDs, including `CodingSchemeUID`, `MappingResourceUID`, `ContextUID`, `TemplateExtensionOrganizationUID`, `SOPClassesInStudy`, `SOPClassesSupported`, `AvailableTransferSyntaxUID`, `StoredInstanceTransferSyntaxUID`, `EncryptedContentTransferSyntaxUID`, and the DICOMDIR attributes `ReferencedSOPClassUIDInFile`, `ReferencedTransferSyntaxUIDInFile` and `ReferencedRelatedGeneralSOPClassUIDInFile` (anonymizing a DICOMDIR therefore corrupts it). It also keeps `ManufacturerDeviceClassUID`, which PS3.15 says to replace (U). The same rule applies to private elements, where the keyword is empty.

Resolution: do not replace a value that is a registered DICOM UID (`value in pydicom.uid.UID_dictionary`, or starts with `1.2.840.10008.`); otherwise replace, unless the attribute is on an explicit keep list. This is value-based, so it also works for private elements and for attributes added to the standard later.

### 🟡 I-8 Private elements are treated differently by transfer syntax

Private elements with PN, UI, DA or DT VR are changed in explicit-VR files; the same elements in an implicit-VR file are read as UN and kept. The same source anonymized in two transfer syntaxes gives two different results. Moot if private elements are removed by default (see roadmap); otherwise use pydicom's private dictionary to resolve VRs where known.

### 🟡 I-9 ID affixes can make every ID identical

The random part is `12 − len(prefix + suffix)` characters. With 12 or more affix characters it is empty, and every ID is `prefix + suffix` (probed). With more than 16 characters, SH attributes such as `AccessionNumber` violate their maximum length. Resolution: reject affixes that leave fewer than, say, 6 random characters, and size the random part per attribute VR (16 for SH, 64 for LO) instead of a fixed 12.

### 🟢 I-10 `StationName` is treated as an ID

It receives the ID format and the `--id-prefix`/`--id-suffix` affixes, so `--id-prefix TEST` changes station names too. Probably fine, but a station-name generator (`CT01`-style, or `STATION_XXXX`) would look more real and keep affixes for IDs. Low priority.

### 🟢 I-11 Address parts are generated independently

`PatientAddress` gets a street only, while `ReferringPhysicianAddress` and `InstitutionAddress` get street, city and country. `RegionOfResidence` gets a city name. Each part is hashed from its own original value, so the city and country of one patient need not agree. `PatientAddress` in DICOM is the whole address, like `ReferringPhysicianAddress`. Resolution: give `PatientAddress` a full address. Coherent city/country pairs are optional realism.

### 🟢 I-12 Name hashing normalizes trailing `^` but not case or whitespace

`DOE^JOHN` and `DOE^JOHN^^^` map to the same pseudonym; `doe^john` and `DOE^JOHN ` (trailing space) map to different ones. Sources do vary in case for the same person. Resolution (**output change**): normalize case and surrounding whitespace before hashing, and possibly ignore ideographic and phonetic groups (`=…`) so that a name written with and without them maps the same.

### 🟢 I-13 `InstitutionName` adds an `InstitutionAddress` that was not there

An object with only `InstitutionName` gains `InstitutionAddress`. This adds information and an attribute. Resolution: only replace an address that is present.

### 🟢 I-14 `--what-if` ignores the other options

It prints `Anonymizer()` defaults, so `--what-if --keep PatientName` still says PN elements are replaced. Resolution: build the anonymizer from all parsed options first, then describe it.

### 💭 I-15 Status attributes over-claim, and one is missing

`PatientIdentityRemoved = YES` is set whenever `BurnedInAnnotation = NO`, although free text, device serial numbers and private data are kept. `LongitudinalTemporalInformationModified` is not set to `MODIFIED` although dates are shifted. Question: should dicognito set `PatientIdentityRemoved` only when the active profile actually meets PS3.15 (so not by default today)? Recommendation: yes, and set `LongitudinalTemporalInformationModified` whenever dates are shifted; write `DeidentificationMethodCodeSequence` (CID 7050) entries only for the profile and options truly applied.

### 💭 I-16 Equal values in different attributes map to equal outputs

`PatientID = 12345` and `AccessionNumber = 12345` both become `9JOO0JZA9C90`. That preserves real equalities (useful: `OtherPatientIDs` equal to `PatientID` stays equal) but also creates the cross-attribute linkage. Question: keep (current) or salt per attribute category? Recommendation: keep, document it.

### 💭 I-17 Re-anonymizing is not idempotent

Running dicognito on its own output changes everything again and pushes dates further back. This is documented for `--in-place`. Question: should dicognito detect `DeidentificationMethod` containing `DICOGNITO` and warn? Recommendation: warn, do not skip. *Tracked as Q13 (2026-11-25).*

## Smaller observations

- `--output-directory` writes a flat directory named by SOP Instance UID; a second object with the same new UID (for example duplicates in the source, or `--keep SOPInstanceUID`) silently overwrites the first. *Tracked as Q14 (2026-11-25).*
- Files without the `DICM` preamble marker are skipped as non-DICOM, logged only at INFO.
- `SOPInstanceUID` cannot be kept independently of `MediaStorageSOPInstanceUID` unless both are kept (`--keep` keys on the tag, and the file meta tag differs).
- `ValueKeeper` accepts only upper-case hex in `gggg,eeee`; `0010,001a` is rejected as an unknown keyword.
- The seed and value are concatenated without a separator before hashing, so seed `a` + value `bc` equals seed `ab` + value `c`. Harmless in practice; fix if the hash is changed anyway.
- MD5 over `seed + value` is used as a keyed pseudorandom function. HMAC-SHA-256 is the conventional construction. Switching changes all output; only worth doing in the same output-change batch, if at all.
