# PS3.15 Table E.1-1 gap analysis

## Method

- Source table: the innolitics `confidentiality_profile_attributes.json` (621 rows), fetched 2026-11-18 from `https://raw.githubusercontent.com/innolitics/dicom-standard/master/standard/confidentiality_profile_attributes.json`. The file does not record which DICOM edition it was parsed from; pin and record the edition before generating code from it.
- For each row with a concrete tag (617 of 621), [tools/probe_table.py](tools/probe_table.py) builds a dataset holding only that element with a sample value of its dictionary VR, runs the default `Anonymizer(seed="probe")`, and records whether the element was removed, emptied, changed, or unchanged. It repeats the run with an empty value. Output: [data/ps315-probe.csv](data/ps315-probe.csv). [tools/analyze_probe.py](tools/analyze_probe.py) summarizes it.
- Not probed: curve data (50xx), overlay comments and data (60xx), and "private attributes" (odd groups). From the code, dicognito keeps all of them except as noted in the behaviour catalogue.
- Single-element datasets understate one behaviour: a TM element alone is never changed, but it is shifted when its paired DA is present. The 53 TM rows are reported separately.
- Column names in the JSON: `basicProfile`, `rtnLongFullDatesOpt`, `rtnLongModifDatesOpt`, `rtnPatCharsOpt`, `rtnDevIdOpt`, `rtnInstIdOpt`, `rtnUIDsOpt`, `rtnSafePrivOpt`, `cleanDescOpt`, `cleanStructContOpt`, `cleanGraphOpt`. There are no columns for Clean Pixel Data or Clean Recognizable Visual Features, which have no per-attribute actions.

## Summary

Rows: Basic Profile action. Columns: what dicognito did to a populated value.

| Basic Profile action | Changed | Emptied | Removed | Sequence kept, items walked | Unchanged | Not probed |
|---|---|---|---|---|---|---|
| D | 35 | 0 | 0 | 5 | 52 | 0 |
| U | 53 | 0 | 0 | 0 | 1 | 0 |
| X | 92 | 2 | 11 | 44 | 231 | 4 |
| X/D | 12 | 0 | 0 | 1 | 9 | 0 |
| X/Z | 2 | 0 | 0 | 2 | 7 | 0 |
| X/Z/D | 4 | 0 | 0 | 2 | 2 | 0 |
| X/Z/U* | 0 | 0 | 0 | 2 | 0 | 0 |
| Z | 14 | 0 | 0 | 5 | 23 | 0 |
| Z/D | 4 | 0 | 0 | 0 | 2 | 0 |
| **Total** | **216** | **2** | **11** | **61** | **327** | **4** |

Of the 327 unchanged, 53 are TM elements that are shifted when paired with their date, leaving **274 attributes that dicognito never changes although the Basic Profile changes, removes or empties them**.

Changed elements by VR: DT 57, DA 55, UI 55, PN 29, LO 12, SH 6, ST 2. In other words, almost all of dicognito's coverage comes from its VR-based handlers; the name-based handlers contribute 20 attributes.

UID coverage is essentially complete: 53 of 54 U rows change. The exception is `ManufacturerDeviceClassUID` (basic U), which the "keyword ends in `ClassUID`" rule skips.

## Where dicognito's action differs in kind from the Basic Profile

These are conformant substitutions or reasonable option-based choices, not gaps:

| Attributes | Basic Profile | Dicognito | Assessment |
|---|---|---|---|
| Names, IDs, institution, addresses where basic is D, Z, Z/D or X/Z/D | Dummy, or zero-length | Realistic pseudonym | Conformant. Table E.1-1a defines D as "a non-zero length value that may be a dummy value and consistent with the VR" and Z as "a zero length value, or a non-zero length value that may be a dummy value and consistent with the VR"; compound codes depend on the attribute's type in the IOD |
| IDs, addresses and other attributes where basic is X | Remove | Realistic pseudonym (`AdmissionID`, `OtherPatientIDs`, `PerformedProcedureStepID`, `RequestedProcedureID`, `ScheduledProcedureStepID`, `ServiceEpisodeID`, `PatientAddress`, `RegionOfResidence`, `CountryOfResidence`, `ReferringPhysicianAddress`, `InstitutionAddress`, …) | Deviation: far better than keeping, but X says remove |
| Dates and date-times (most are X, X/Z or Z in basic) | Remove or empty | Shift | Matches Retain Longitudinal Temporal Information with Modified Dates (`rtnLongModifDatesOpt = C`), except that `LongitudinalTemporalInformationModified` is not set |
| `PatientBirthDate` (Z), `PatientBirthTime` (X) | Empty, remove | Shift | Matches the Modified Dates option for the date. `PatientBirthTime` has no option-based retention; the profile always removes it |
| `PatientID` (Z/D), `AccessionNumber` (Z), `StudyID` (Z) | Empty or dummy | Pseudonym | Conformant (Z permits a dummy value), and exactly what test-data users rely on |
| `IssuerOfPatientID` (X) | Remove | `DICOGNITO` | Deviation; also collapses distinct issuers (see inconsistencies) |
| `InstitutionalDepartmentName` (X) | Remove | `RADIOLOGY` | Deviation |

## Unchanged attributes, grouped by the option that governs them

The full list, with VRs and all option columns, is in [data/ps315-probe.csv](data/ps315-probe.csv) (rows with `populated = unchanged`). Groups below use each attribute's option columns.

### Free text and descriptors (Clean Descriptors option `C`; Basic mostly X)

About 120 attributes. The ones that matter most for imaging test data:

| Category | Attributes |
|---|---|
| Study, series, protocol | `StudyDescription`, `SeriesDescription`, `ProtocolName`, `PerformedProcedureStepDescription`, `ScheduledProcedureStepDescription`, `RequestedProcedureDescription`, `RequestedSeriesDescription`, `AcquisitionProtocolDescription`, `DerivationDescription`, `AcquisitionDeviceProcessingDescription` |
| Comments and history | `AdditionalPatientHistory`, `PatientComments`, `StudyComments`, `ImageComments`, `FrameComments`, `AcquisitionComments`, `VisitComments`, `RequestedProcedureComments`, `ImagingServiceRequestComments`, `CommentsOnThePerformedProcedureStep`, `CommentsOnRadiationDose`, `IdentifyingComments`, `ResultsComments`, `Impressions`, `InterpretationText` |
| Reasons and diagnoses | `ReasonForStudy`, `ReasonForVisit`, `ReasonForTheRequestedProcedure`, `ReasonForTheImagingServiceRequest`, `AdmittingDiagnosesDescription`, `DischargeDiagnosisDescription`, `InterpretationDiagnosisDescription` |
| Patient clinical text | `MedicalAlerts`, `Allergies`, `PatientState`, `SpecialNeeds`, `PreMedication` (some also governed by Retain Patient Characteristics) |
| Radiotherapy labels and descriptions | `RTPlanName`, `RTPlanLabel`, `RTPlanDescription`, `StructureSetName`, `StructureSetLabel`, `StructureSetDescription`, `ROIName`, `ROIDescription`, `BeamDescription`, `PrescriptionDescription`, `FractionationNotes`, … |
| Contrast | `ContrastBolusAgent`, `RequestedContrastAgent` |

Test-data users need `StudyDescription`, `SeriesDescription`, `ProtocolName` and `BodyPartExamined` (the last is not in the table) for hanging protocols and routing. This is the main tension with a conformant default.

### Device identity (Retain Device Identity option `K`; Basic X or D)

`DeviceSerialNumber`, `DetectorID`, `XRayDetectorID`, `XRaySourceID`, `GantryID`, `GeneratorID`, `PlateID`, `CassetteID`, `DeviceDescription`, `DeviceLabel`, `UniqueDeviceIdentifier`, `ManufacturerDeviceIdentifier`, `ModifyingDeviceID`, `ModifyingSystem`, `SourceSerialNumber`, `SourceManufacturer`, `TreatmentMachineName`, `PerformedStationName`, `ScheduledStationName`, `ScheduledStudyLocation`, `ScheduledProcedureStepLocation`, `LensMake`, `LensModel`, `LensSerialNumber`, `LensSpecification`, `XRayDetectorLabel`, calibration dates and times. Also `ManufacturerDeviceClassUID` (U).

AE titles (Retain Device Identity option `C`; Basic X or D): `StationAETitle`, `RetrieveAETitle`, `PerformedStationAETitle`, `ScheduledStationAETitle`, `ScheduledStudyLocationAETitle`, `NetworkID`, `Originator`, `DestinationAE`, `ReceivingAE`, `RequestingAE`, `SelectorAEValue`. `RetrieveURL` (UR) is not in this version of the table at all, but it carries host names and original UIDs; dicognito keeps it (probed), so a retained URL also points back to the original study. Attributes outside the table that dicognito should consider anyway are a separate list to build (start with `RetrieveURL`, `RetrieveURI`, `IssuerOfPatientIDQualifiersSequence` contents such as `UniversalEntityID`).

### Patient characteristics (Retain Patient Characteristics option `K`; Basic X or Z)

`PatientAge`, `PatientSex`, `PatientSexNeutered`, `PatientSize`, `PatientWeight`, `EthnicGroup`, `SmokingStatus`, `PregnancyStatus`, `SelectorASValue`. Test data needs these; a dicognito default would retain them via this option.

### Institution identity (Retain Institution Identity option `K`)

`ClinicalTrialSiteID`, `ClinicalTrialSiteName`, `ClinicalTrialCoordinatingCenterName`, `ClinicalTrialProtocolEthicsCommitteeName`, `SourceOfPreviousValues`. (Dicognito already pseudonymizes `InstitutionName` and `InstitutionAddress`.)

### Identifiers and issuers with no retention option (Basic X, Z or D)

`IssuerOfAdmissionID`, `IssuerOfServiceEpisodeID`, `StudyIDIssuer`, `InterpretationID`, `InterpretationIDIssuer`, `ResultsID`, `ResultsIDIssuer`, `InsurancePlanIdentification`, `SpecimenAccessionNumber`, `SpecimenIdentifier`, `ContainerIdentifier`, `ContainerComponentID`, `SlideIdentifier`, clinical-trial IDs (`ClinicalTrialSubjectID`, `ClinicalTrialSubjectReadingID`, `ClinicalTrialProtocolID`, `ClinicalTrialSeriesID`, `ClinicalTrialTimePointID` and their issuers), `BarcodeValue`, `LabelText`, `DeviceAlternateIdentifier`.

Several of these are natural candidates for dicognito's ID pseudonymizer rather than removal: `ClinicalTrialSubjectID`, `SpecimenIdentifier`, `ContainerIdentifier`, `InterpretationID`, `ResultsID`.

### Contact and location (Basic X)

`PersonAddress`, `PersonTelephoneNumbers`, `PersonTelecomInformation`, `OrderCallbackPhoneNumber`, `OrderCallbackTelecomInformation`, `OrderEntererLocation`, `PerformedLocation`, `RequestedProcedureLocation`, `PatientInstitutionResidence`, `ScheduledPatientInstitutionResidence`, `PatientTransportArrangements`, `DistributionAddress`, `TelephoneNumberTrial`, `AddressTrial`, `HumanPerformerOrganization`, `VerifyingOrganization`, `CameraOwnerName`, `TopicAuthor`. All GPS attributes (`GPSLatitude`, `GPSLongitude`, …).

`PersonAddress` and `PersonTelephoneNumbers` sit in person identification sequences next to names that dicognito does pseudonymize, so the name is replaced but the person's address and phone are kept.

### Temporal (Modified Dates option `C`)

53 TM attributes, shifted only when the paired DA is present. `TimezoneOffsetFromUTC` (option C) is kept; it can narrow down a site's location. `CertifiedTimestamp` and `FrameOriginTimestamp` (OB) are kept.

### Binary and signatures (Basic X or D)

`EncapsulatedDocument` (D; can contain an entire identifying PDF or CDA), `DigitalSignaturesSequence` content, `CertificateOfSigner`, `MAC`, `DataSetTrailingPadding`, `MakerNote`, `NonconformingDataElementValue`, `IconImageSequence` (kept with items walked; it is a thumbnail of the pixel data).

`OriginalAttributesSequence`, `ModifiedAttributesSequence` and `NonconformingModifiedAttributesSequence` are kept with items walked: PN, UI, DA and DT inside them are changed, but original text values are not.

### Structured content (Clean Structured Content option `C`)

`ContentSequence`, `AcquisitionContextSequence`: kept, items walked. PN, UI, DA and DT content items are changed; TEXT (`TextValue`), CODE meanings, NUM and TIME items are kept.

### Graphics (Clean Graphics option `C`)

`GraphicAnnotationSequence` (kept, items walked; `TextValue`/`UnformattedTextValue` inside are kept), overlay data and comments (60xx), curve data (50xx).

### Private attributes (Retain Safe Private option)

All kept except the Mitra global patient ID; explicit-VR PN, UI, DA and DT private elements are changed.

## Empty values

Of 554 non-sequence attributes probed with an empty value, 531 stay empty, 9 are removed (the stripper list) and 14 become populated: the 12 ID attributes and `StationName` (all to the same generated ID), `InstitutionName` (a generated clinic name, plus a generated `InstitutionAddress`) and `InstitutionalDepartmentName` (`RADIOLOGY`). See [05-empty-attributes.md](05-empty-attributes.md).

## Implications for a profile engine

1. The Basic Profile table maps cleanly onto dicognito if each action code is implemented by a dicognito action: D → realistic pseudonym when the VR or attribute has a generator, else a VR-appropriate dummy; U → `2.25.` UID; X → remove; Z → empty; K → keep; C → clean (see roadmap); compound codes (X/Z, X/D, Z/D, X/Z/D, X/Z/U*) → choose by the attribute's type in the IOD, or, since dicognito does not know the IOD, by a fixed rule (prefer the rightmost non-removing action, so that Type 1 and Type 2 attributes stay present).
2. The VR-based handlers should stay as a safety net for attributes not in the table (for example new attributes, and private elements with known VRs, if private elements are retained).
3. Dicognito's current default corresponds roughly to: Basic Profile + Retain Longitudinal Temporal Information with Modified Dates + Retain Patient Characteristics + Retain Device Identity + Retain Safe Private (all private) + keep descriptors + keep structured text + keep graphics, with pseudonyms for D and some Z/X attributes. Writing that down as an explicit profile is the first step towards making the deviations a choice rather than an accident.
