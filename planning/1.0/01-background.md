# Dicognito background: mission, strengths, weaknesses, landscape

This is the working background statement for planning dicognito 1.0. It is deliberately candid. The public blurb at the end is derived from it.

## Mission

Dicognito turns real DICOM data into realistic, internally consistent, de-identified data. Every identifying value it recognizes is replaced by a plausible fake, and the relationships between patients, studies, series, instances, references and dates survive the change.

## Goals

1. **Preserve relationships.** Objects anonymized with one `Anonymizer` (one CLI run) stay grouped in the same patients, studies and series. References between objects (for example `ReferencedSOPInstanceUID` in any sequence, `MediaStorageSOPInstanceUID` in the file meta) still resolve. Intervals between dates are preserved. Across separate runs, the same `--seed` reproduces the same mapping.
2. **Look like real data.** Replacements have the shape of real values: person names with family, given and middle components, 12-character IDs, street addresses, clinic names, dates in the plausible past and conformant UIDs. Software that consumes the output (PACS, viewers, worklists, routers, AI pipelines) behaves as it would on real data.
3. **Work with no configuration.** `dicognito -o out in` is a complete, useful command. The library is a small, embeddable API over pydicom.
4. **Be transparent.** `--what-if` and the README list every action. Behaviour is deterministic given a seed.
5. **Produce valid DICOM.** Output should be readable by any DICOM toolkit and should not introduce VR or VM violations.
6. **Stay light.** Pure Python, one runtime dependency (pydicom), typed.

## Non-goals (today)

- Inspecting or modifying pixel data (see the pixel-data section of [07-roadmap.md](07-roadmap.md) for the argument and a possible plan).
- Natural-language analysis of free text.
- Holding a re-identification key. Dicognito is stateless; it keeps no mapping table.
- Formats other than DICOM.
- Certifying compliance with any regulation. Dicognito can implement a documented profile; whether that profile satisfies HIPAA, GDPR, PHIPA or an IRB is the user's determination.

## Primary and secondary audiences

| Audience | Workflow | Why dicognito fits |
|---|---|---|
| Builders and testers of imaging software (primary) | Turn real studies into test data for PACS, viewers, routers, AI pipelines; load-test with many distinct synthetic patients (one seed per copy) | Worklists, patient search, sorting, prior-study matching, hanging protocols and reference navigation keep working because values are pseudonymized, not blanked |
| Support and integration engineers | Share a problem study with a vendor or another team without sharing the patient | One command, structure preserved, so the problem usually reproduces |
| Researchers and clinical-trial data managers (secondary) | Pseudonymize headers for an internal or trusted research environment | Consistent pseudonyms and shifted dates keep longitudinal relationships; seed gives reproducibility |
| Teaching-file authors | Strip identity from interesting cases | Realistic output reads naturally in a viewer |

## Strengths (honest, by workflow)

- **Pseudonymization instead of blanking.** Most de-identification approaches remove or blank names, IDs and dates by default. Dicognito replaces them with consistent, realistic values, which is what test-data and integration workflows need.
- **Relationships survive without a state file.** Replacement values are a keyed hash of the original value (seed plus value), so equal inputs always produce equal outputs within a run, and across runs with the same seed. No mapping table is written to disk, so there is nothing extra to secure.
- **Coverage by value representation, not only by name.** Every PN, UI, DA and DT element is handled wherever it appears: top-level, inside any sequence (including SR content items and `OtherPatientIDsSequence`), and in private elements whose VR is known. New attributes added to the standard are covered automatically.
- **Conformant, consistent UIDs.** Replacement UIDs are UUID-derived `2.25.` UIDs (PS3.5 B.2), merged to `main` in #191 and due in the next release from `main`; well-known class and transfer-syntax UIDs are left alone.
- **Interval-preserving dates.** One offset (62 to 730 days into the past) applies to all dates in a run, so ages, intervals between priors and study ordering are preserved. Partial dates and date-times with time-zone suffixes are handled.
- **Simple extension.** `Anonymizer.add_element_handler` lets callers override or add behaviour per element; `--keep` exposes the common case on the command line.
- **Small and dependable footprint.** One dependency, typed, fast enough for directory trees, Python 3.11 to 3.15 (3.15 added on `main` in #187, unreleased).

## Weaknesses (honest)

These are the gaps a careful user needs to know about. The detail is in [03-ps315-gap-analysis.md](03-ps315-gap-analysis.md) and [04-inconsistencies.md](04-inconsistencies.md).

- **Allow-list for everything except PN, UI, DA and DT.** Of the 617 attributes in DICOM PS3.15 Table E.1-1 that can be probed directly, dicognito leaves 274 unchanged (plus 53 times that change only when paired with a date). They include free text (`StudyDescription`, `SeriesDescription`, `ProtocolName`, `AdditionalPatientHistory`, `PatientComments`, `ImageComments`, `StudyComments`, `ReasonForStudy`, …), device identifiers (`DeviceSerialNumber`, `DetectorID`, `GantryID`, `PlateID`, …), AE titles and `RetrieveURL` (which carry host names), clinical-trial attributes, specimen identifiers, patient characteristics (`PatientAge`, `PatientSex`, `PatientWeight`, `PatientSize`, `EthnicGroup`) and GPS attributes.
- **Private attributes are kept.** Except for the Mitra global patient ID, private elements are kept. Private elements with explicit PN, UI, DA or DT VRs are changed, but the same elements in an implicit-VR file are read as UN and kept, so results depend on the transfer syntax.
- **Overlays and curves are kept.** Overlay data and overlay comments (groups 60xx) and curve data (50xx) pass through unchanged.
- **No pixel-data handling.** Only a guard on the `BurnedInAnnotation` attribute, which warns by default.
- **The seed is a key.** With the seed, anyone can recompute the pseudonym of a guessed original value. Medical record numbers and dates have small value spaces, so a leaked seed allows dictionary attacks. Omitting the seed uses a random one per run.
- **One global date offset.** Every patient in a run is shifted by the same amount, and the offset is bounded (62 to 730 days). Knowing one real date for one object reveals the offset for all; and every real date is known to within about two years.
- **Realistic fakes can be mistaken for real people or real data.** Generated names are common names, so they will match real people. An ID prefix or suffix (`--id-prefix`) helps label synthetic data.
- **Status markers over-claim.** `PatientIdentityRemoved` is set to `YES` whenever `BurnedInAnnotation` is `NO`, even though free text and private data may still identify the patient. `LongitudinalTemporalInformationModified` is not set although dates are shifted. No `DeidentificationMethodCodeSequence` is written.
- **No audit output.** There is no per-run record of what was changed, kept or removed beyond the summary table.
- **Brittle on malformed input.** Some malformed values (for example a `00000000` date, which real modalities emit) raise an exception, and the command line aborts the whole run.

## Position relative to the DICOM standard

DICOM PS3.15 Annex E defines the Basic Application Level Confidentiality Profile (Table E.1-1, action codes D dummy, Z zero-length, X remove, K keep, C clean, U new UID) and options that retain or clean particular groups of attributes (Retain Longitudinal Temporal Information with Full or Modified Dates, Retain Patient Characteristics, Retain Device Identity, Retain Institution Identity, Retain UIDs, Retain Safe Private, Clean Descriptors, Clean Structured Content, Clean Graphics, Clean Pixel Data, Clean Recognizable Visual Features).

Several of dicognito's actions are already conformant ways of performing the standard's actions:

| Standard action | Dicognito today | Conformant? |
|---|---|---|
| D (dummy value consistent with the VR) | Realistic pseudonym for PN, IDs, institution, address | Yes: a realistic fake is a dummy value |
| U (new, internally consistent UID) | `2.25.` UUID-derived UID, consistent within a run | Yes (on `main` since #191; released versions up to 0.19.1 use `2.` plus 40 digits) |
| Retain Longitudinal Temporal Information, Modified Dates | Shift all DA/DT (and paired TM) by one offset | Yes in spirit; the option also requires `LongitudinalTemporalInformationModified = MODIFIED`, which is not set |
| X (remove) | 11 attributes removed | Yes, for those 11 |
| Z (zero-length) | `RequestingService`, `CurrentPatientLocation` emptied | Yes |

What prevents a conformance claim is coverage (attributes the Basic Profile removes or cleans that dicognito keeps), private and overlay data, and the missing status attributes. Closing those gaps while keeping test-data-friendly defaults is the central design question for 1.0; see [07-roadmap.md](07-roadmap.md).

## Capability landscape

Other de-identification tools offer capabilities dicognito does not. This table records the capabilities, not the tools' shortcomings. Entries are drawn from each project's public documentation; those marked "unverified" could not be confirmed from primary documentation during this review.

| Capability | Offered by (examples) | Dicognito today | Consider for dicognito? |
|---|---|---|---|
| Declarative rule file per attribute (keep, remove, blank, replace, regex) | pydicom/deid recipes; RSNA CTP anonymizer scripts; KitwareMedical dicom-anonymizer JSON dictionaries; Orthanc `Keep`/`Replace`/`Remove`; XNAT DicomEdit | `--keep` only; Python handlers | 1.x: small config file (TOML) for keep/remove/blank overrides. Not needed for 1.0 |
| Built-in PS3.15 Basic Profile, selectable standard edition | Orthanc (`DicomVersion`: 2008, 2017c, 2021b, 2023b); KitwareMedical dicom-anonymizer; gdcmanon | No | Yes: generated table, edition pinned and recorded |
| PS3.15 options as switches | dcm4chee-arc (`RetainUIDsOption`, `RetainDeviceIdentityOption`, …); a `deidentify` CLI with `--retain-uid/--retain-date/--retain-dev/--retain-org` (unverified provenance) | No | Yes |
| Private attributes removed by default, with a keep switch | KitwareMedical dicom-anonymizer (`--keepPrivateTags`); Orthanc (`KeepPrivateTags`); deid default recipe | Kept | Yes, with an escape hatch |
| Safe-private allow-list by private creator | RSNA CTP; PS3.15 Retain Safe Private option | No | Yes |
| Lookup table mapping real IDs to assigned IDs (for example MRN to trial subject ID) | RSNA CTP `@lookup` | No | 1.x: `--map file.csv` for IDs; complements seeds |
| Date shift keyed per patient | RSNA CTP `@hashdate(this, PatientID)` | One offset per run | Consider as an option: stronger privacy, but breaks cross-patient time alignment |
| UID root owned by the user | RSNA CTP `@hashuid(root, this)` | Fixed `2.25.` | Low value; `2.25.` needs no registered root |
| Encrypted original attributes for authorized re-identification | gdcmanon (PKCS#7, Encrypted Attributes Sequence) | No | Non-goal |
| Compliance manifest and residual-PHI scan | dcm-anon (Ces107) | No | Yes, a light version: JSON report, plus an "echo" scan for original identifiers left in free text (see roadmap) |
| Header-based filters and quarantine | deid `%filter`; RSNA CTP filter stages | `BurnedInAnnotation` guard (warn or fail) | 1.0: widen the guard's heuristics; 1.x: `--skip`/`--quarantine-dir` |
| Pixel redaction (fixed regions, OCR) | deid; RSNA CTP pixel anonymizer; PixelMed DicomCleaner; cloud healthcare APIs | No | Deferred; see roadmap |
| Server and pipeline integration | Orthanc; RSNA CTP; dcm4chee-arc | No | Non-goal |

Sources: [Orthanc Book, anonymization](https://orthanc.uclouvain.be/book/users/anonymization.html); [dcm4chee-arc wiki, Anonymize Data on Retrieve](https://github-wiki-see.page/m/dcm4che/dcm4chee-arc-light/wiki/Anonymize-Data-on-Retrieve); [dicom-anonymizer on PyPI](https://pypi.org/project/dicom-anonymizer); [RSNA CTP user group, UID hashing](https://groups.google.com/g/rsnas-ctpmirc-user-group/c/KtzbafKiV8I); [RSNA COVID-19 de-identification protocol](https://www.rsna.org/-/media/Files/RSNA/Covid-19/RICORD/RSNA-Covid-19-Deidentification-Protocol.pdf); [gdcmanon man page](https://manpages.debian.org/jessie/libgdcm-tools/gdcmanon.1.en.html); [dcm-anon](https://github.com/Ces107/dcm-anon); [pydicom/deid](https://pydicom.github.io/deid/).

## Corrections to claims from an external AI conversation

The planning conversation that preceded this document included several claims about dicognito. Checked against the code and a probe of the current branch:

| Claim | Finding |
|---|---|
| `OtherPatientIDsSequence` is not anonymized | It is: `PatientID` and `IssuerOfPatientID` inside its items are handled, because handlers run on every element in every sequence |
| `AdmissionID` and `IssuerOfAdmissionID` are missed | `AdmissionID` is handled on `main` (unreleased). `IssuerOfAdmissionID` is still kept |
| Private tags are untouched except the Mitra ID | Partly wrong: private elements with explicit PN, UI, DA or DT VR are changed; others are kept |
| Structured reports are not scrubbed | Partly wrong: PNAME, UIDREF, DATE and DATETIME content items are changed. TEXT items and TIME items are kept |
| `add_element_handler` appends a handler | It inserts at the front, so the new handler wins. Handlers return `bool` (`True` stops further handlers) |
| A mapping export could read dicognito's existing lookup dictionaries | Dicognito keeps no lookup dictionaries; values are hashed on demand. A mapping export would have to record pairs as they are produced |
| A mapping export was discussed with "Dr. Woodard" | Correct: [issue #124](https://github.com/blairconrad/dicognito/issues/124), closed for lack of follow-up |
| `--seed $i` in a loop produces distinct synthetic patients from one source study | Correct |

## Public blurb (draft)

For the top of the README and the package description. It leads with test data, states the limits plainly, and avoids compliance claims.

> **Dicognito** anonymizes DICOM files and keeps them useful. It replaces names, IDs, addresses, institutions and UIDs with realistic, consistent stand-ins and shifts dates into the past, so anonymized objects still group into the same patients, studies and series, still reference one another, and still look like real clinical data to the software that reads them.
>
> Use it to turn real studies into test data for PACS, viewers and imaging pipelines, to share a problem study with a vendor, or as the pseudonymization step in a research workflow. Run it from the command line with no configuration, or call it from Python.
>
> Dicognito changes header data only. It does not inspect pixel data, and by default it keeps free-text descriptions and private attributes, which can contain identifying information. Review [exactly what dicognito changes](#exactly-what-does-dicognito-do) before sharing its output outside your organization.

One-line package description: *Anonymize DICOM files into realistic, consistent test data.*

The third paragraph must change as the 1.0 work lands (for example once private attributes are removed by default).
