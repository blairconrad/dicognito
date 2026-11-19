# Dicognito behaviour catalogue

Current behaviour of dicognito, read from the source on branch `fix/conformant-uis` (which is `main` plus the conformant-UID change) and confirmed with probe scripts in [tools/](tools/). Where a statement comes from reading the code and was not probed, it says so.

## Processing model

- `Anonymizer.anonymize(dataset)` walks `dataset.file_meta`, then the dataset, recursively through every sequence item (pydicom `Dataset.walk`).
- For each element, the element handlers run in order. The first handler that returns `True` claims the element and later handlers are skipped. A handler may change other elements in the same dataset (the date handler changes the paired time; the institution-name handler sets the institution address).
- `add_element_handler(h)` inserts `h` at the front, so it takes precedence over the defaults. `ValueKeeper` (used by `--keep`) works this way: it claims the element and does nothing.
- After the walk, dataset updaters run once on the top-level dataset only.
- A handler sees the dataset that directly contains the element. For an element in a sequence item, that is the item, not the top-level dataset.

## Randomness and determinism

- `Randomizer(seed)`: if `seed` is `None`, the seed is `str(os.urandom(20))`; otherwise `str(seed)`.
- A value maps to `md5(seed + original_value)` as a big integer, which is then split into indices. The seed and value are concatenated with no separator.
- All handlers share one randomizer, so equal original strings in different attributes produce related output. For IDs, an equal value in `PatientID`, `AccessionNumber`, `StudyID` and `StationName` maps to the same new ID (probed).
- Date offset: `-(to_int("date_offset") % (730*24 − 62*24) + 62*24)` hours, so 62 to 730 days into the past, in whole hours (probed over 2,000 seeds: 63 to 730 whole days of date shift).
- UIDs: `2.25.<uuid5(uuid5(DICOGNITO_NAMESPACE, seed), original_uid).int>`. On `main` before the fix: `"2." + str(10**39 + md5int)`.

## Default element handlers, in order

| # | Handler | Applies to | Action | Empty value | Notes |
|---|---|---|---|---|---|
| 1 | `UnwantedElementsStripper` | `BranchOfService`, `Occupation`, `MedicalRecordLocator`, `MilitaryRank`, `PatientInsurancePlanCodeSequence`, `PatientReligiousPreference`, `PatientTelecomInformation`, `PatientTelephoneNumbers`, `ReferencedPatientPhotoSequence`, `ReferringPhysicianTelephoneNumbers`, `ResponsibleOrganization` | Remove | Removed | Anywhere in the tree |
| 2 | `UIAnonymizer` | Any element with VR UI, except keywords ending in `ClassUID` and `TransferSyntaxUID` | Replace with `2.25.` UID, each value of a multi-valued element separately | Kept empty (handler declines, later handlers also decline) | 97 dictionary UI keywords are replaced, including 24 that hold registry UIDs (see inconsistencies). Applies to file meta (`MediaStorageSOPInstanceUID` maps to the same value as `SOPInstanceUID`) and to private elements with VR UI |
| 3 | `PNAnonymizer` | Any element with VR PN | Replace with `LAST^FIRST^MIDDLE` from US census name lists; first name from the female list if the containing dataset's `PatientSex` is `F`, the male list if `M`, else the combined list; middle name always from the combined list | Kept empty | Original is `rstrip("^")`-ed before hashing, so `DOE^JOHN^^^` equals `DOE^JOHN`; case and other whitespace are significant. Multi-valued: each value separately. Ideographic and phonetic groups are discarded |
| 4 | `IDAnonymizer` | `AccessionNumber`, `AdmissionID`, `OtherPatientIDs`, `FillerOrderNumberImagingServiceRequest`, `FillerOrderNumberImagingServiceRequestRetired`, `FillerOrderNumberProcedure`, `PatientID`, `PerformedProcedureStepID`, `PlacerOrderNumberImagingServiceRequest`, `PlacerOrderNumberImagingServiceRequestRetired`, `PlacerOrderNumberProcedure`, `RequestedProcedureID`, `ScheduledProcedureStepID`, `ServiceEpisodeID`, `StationName`, `StudyID`; plus `IssuerOfPatientID`; plus private Mitra global patient ID | ID: `prefix + random[A-Z0-9] + suffix`, 12 characters in total. `IssuerOfPatientID`: `DICOGNITO`. Mitra (0031,xx20 under creator `MITRA LINKED ATTRIBUTES 1.0`): VR forced to LO, bytes decoded as ASCII, then replaced like an ID | IDs: **replaced with a generated value** (every empty ID maps to the same value for a seed). `IssuerOfPatientID`: kept empty. A `None` value raises `TypeError` | `--id-prefix`/`--id-suffix` reduce the random part; at 12 or more affix characters all IDs are identical (probed) |
| 5 | `AddressAnonymizer` | `PatientAddress` (street only), `RegionOfResidence` (city name), `CountryOfResidence` (country), `ReferringPhysicianAddress` (street, city, country) | Replace | Kept empty | Each derived from its own original value, so the parts need not agree |
| 6 | `EquipmentAnonymizer` | `InstitutionName`, `InstitutionAddress`, `InstitutionalDepartmentName` | Name: `<CITY>'S <STREET> CLINIC`, and sets `InstitutionAddress` to a full address derived from the original name (adds it if absent). Address alone: full address, only if `InstitutionName` is absent. Department: `RADIOLOGY` | Name: **generated name and address**. Address: kept empty. Department: **`RADIOLOGY`** | `--keep InstitutionName` also keeps `InstitutionAddress` (tested) |
| 7 | `FixedValueAnonymizer` | `RequestingService`, `CurrentPatientLocation` | Set to `""` | `""` | |
| 8 | `DateTimeAnonymizer` | Any element with VR DA or DT | DA: shift by the offset; if the element whose keyword is the DA keyword with `Date` replaced by `Time` is present and non-empty, shift date and time together as one instant and write both. DT: shift as an instant, keeping precision and any time-zone suffix. ACR-NEMA `YYYY.MM.DD` and `HH:MM:SS` forms accepted and written without separators | Kept empty | TM elements are only changed through their paired DA. Date-only values are shifted as if at midnight (see inconsistencies). Invalid values raise and abort (probed: `UNKNOWN`, `00000000`, `20200230`, a range, an empty component of a multi-valued date) |

Everything else is kept unchanged. That includes all elements with VRs LO, SH, LT, ST, UT, UC, CS, AE, AS, UR, numeric VRs, binary VRs and UN, except those named above; all private elements except as noted; overlay and curve groups; and TM elements without a paired, non-empty DA.

## Dataset updaters (top level, after the walk)

| Updater | Behaviour |
|---|---|
| `DeidentificationMethodUpdater` | If absent or empty: set `DeidentificationMethod` to `DICOGNITO`. If present and does not already contain `DICOGNITO`: append it (making it multi-valued; VM 1-n is allowed). Always added, so it is the one attribute dicognito adds to every object |
| `PatientIdentityRemovedUpdater` | If `BurnedInAnnotation` is exactly `NO`, set `PatientIdentityRemoved` to `YES`. Otherwise leave it as it is (including an existing `NO`) |

Not written: `DeidentificationMethodCodeSequence`, `LongitudinalTemporalInformationModified`.

## Public Python API (as it stands)

| Item | Notes |
|---|---|
| `dicognito.__version__` | Only name in `__all__` |
| `dicognito.anonymizer.Anonymizer(id_prefix="", id_suffix="", seed=None)` | `anonymize(dataset)`, `describe_actions()`, `add_element_handler(handler)` |
| `dicognito.element_anonymizer.ElementAnonymizer` | Base class: `__call__(dataset, data_element) -> bool`, `describe_actions() -> Iterator[str]` |
| `dicognito.value_keeper.ValueKeeper(tag_name)` | Keyword or `gggg,eeee` (upper-case hex only) |
| `dicognito.exceptions.TagError` | Raised by `ValueKeeper` |
| Handler modules (`pnanonymizer`, `idanonymizer`, `uianonymizer`, `datetimeanonymizer`, `addressanonymizer`, `equipmentanonymizer`, `fixedvalueanonymizer`, `unwantedelements`), `randomizer`, `dataset_updater`, `pipeline`, `filters`, `_config` | Importable, with no underscore, so implicitly public; not documented as public. 1.0 must decide |

## Command line

| Option | Behaviour |
|---|---|
| `sources` (one or more) | File, directory (recursed with `os.walk`) or glob. Files are read with `force=False`; a file pydicom rejects as non-DICOM (for example one without the `DICM` preamble marker) is skipped with an INFO log |
| `-o/--output-directory DIR` | Write each object to `DIR/<new SOPInstanceUID>.dcm` (flat; created if needed; an existing file with the same name is overwritten) |
| `-i/--in-place` | Overwrite the source files |
| neither | Warn, then behave as `--in-place` (the 0.15.0 release notes promise this becomes an error) |
| `-p/--id-prefix`, `-s/--id-suffix` | Affixes for IDs (and `StationName`) |
| `--seed` | Seed the randomizer |
| `--keep ELEM` (repeatable) | Add a `ValueKeeper` for a keyword or upper-case `gggg,eeee` tag, everywhere in the tree |
| `--assume-burned-in-annotation {if-yes,unless-no,never}` | Default `if-yes` |
| `--on-burned-in-annotation {warn,fail}` | Default `warn`; `fail` aborts the run |
| `-q/--quiet` | Suppress the summary table (sorted unique `AccessionNumber`, `PatientID`, `PatientName` rows, printed as a Markdown table) |
| `--log-level` | Default `WARNING` |
| `--what-if` | Print the default `Anonymizer()` actions and exit; ignores every other option, including `--keep` and affixes |
| `--version` | Platform, Python, dicognito and pydicom versions |

Error handling: any exception while anonymizing or saving one file logs the file name and exits with status 1, leaving earlier files written (or overwritten, with `--in-place`) and later files untouched.

Release defect: the `dicognito` console command in 0.19.0 fails at start-up with `TypeError: main() missing 1 required positional argument: 'main_args'` (confirmed with `uvx --from dicognito==0.19.0 dicognito --version`; 0.18.0 works). Commit `9ffc4bb` ("Fix new type-checking errors") removed the default argument. `python -m dicognito` still works. The tests call `main(args)` directly, so they did not catch it.

## Behaviour by value representation (summary)

| VR | Dicognito | Notes |
|---|---|---|
| PN | Pseudonym | Everywhere, including private explicit-VR and SR `PersonName` |
| UI | New `2.25.` UID | Except keywords ending `ClassUID` and `TransferSyntaxUID` |
| DA | Shifted | With paired TM |
| DT | Shifted | |
| TM | Shifted only with its paired DA | SR `Time` items, `SeriesTime` without `SeriesDate`, and so on are kept |
| LO, SH | 16 ID-like attributes, 6 address and institution attributes; rest kept | |
| LT, ST, UT, UC | `InstitutionAddress`, `ReferringPhysicianAddress`; rest kept | All free text kept |
| AE, UR, AS, CS, numeric, binary, UN | Kept | |
| SQ | Kept; items processed recursively | Except the two removed sequences |
