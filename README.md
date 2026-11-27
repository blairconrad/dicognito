![Dicognito logo](https://github.com/blairconrad/dicognito/raw/main/assets/dicognito_128.png "Dicognito logo")

Dicognito is a [Python](https://www.python.org/) module and command-line utility that anonymizes
[DICOM](https://www.dicomstandard.org/) files.

Use it to anonymize one or more DICOM files belonging to one or any number of patients. Objects will remain grouped
in their original patients, studies, and series.

Anonymization causes significant elements, such as identifiers, names, and
addresses, to be replaced by new values. Dates and times will be shifted into the
past, but their order will remain consistent within and across the files.

The package is [available on pypi](https://pypi.org/project/dicognito/) and can be installed from the command line by typing

```
pip install dicognito
```

## Anonymizing from the command line

Once installed, a `dicognito` command will be added to your Python scripts directory.
You can run it on entire filesystem trees or a collection of files specified by glob like so:

```bash
# Recurse down the filesystem, anonymizing all found DICOM files.
# Anonymized files will be placed in out-dir, named by new SOP
# instance UID.
dicognito --output-directory out-dir .

# Anonymize all files in the current directory with the dcm extension
# (-o is an alias for --output-directory).
dicognito -o out-dir *.dcm

# Anonymize all files in the current directory with the dcm extension
# but overwrite the original files.
# Note: repeatedly anonymizing the same files will cause date elements
# to  move farther into the past.
dicognito --in-place *.dcm
```
Get more help via `dicognito --help`.

## Anonymizing from within Python

To anonymize a bunch of DICOM objects from within a Python program, import the objects using
[pydicom](https://pydicom.github.io/) and use the `Anonymizer` class:

```python
import pydicom
import dicognito.anonymizer

anonymizer = dicognito.anonymizer.Anonymizer()

for original_filename in ("original1.dcm", "original2.dcm"):
    with pydicom.dcmread(original_filename) as dataset:
        anonymizer.anonymize(dataset)
        dataset.save_as("clean-" + original_filename)
```

Use a single `Anonymizer` on datasets that might be part of the same series, or the identifiers will not be
consistent across objects.

Additional (even custom) element handlers can be added to the `Anonymizer` via `add_element_handler` to augment
or override builtin behavior.

## Versioning and output stability

Dicognito uses [Intended Effort Versioning](https://jacobtomlinson.dev/effver/) (Macro.Meso.Micro), so a release's number reflects the effort an existing user can expect to spend adopting it. While dicognito is below 1.0, versions read as `0.Macro.Micro`: a change that would be meso also bumps the middle number, so only micro releases are safe to take without reading the notes. Releases before 0.20.0 were not numbered this way. The reasoning is recorded in [ADR 2](https://github.com/blairconrad/dicognito/blob/main/docs/adr/0002-intended-effort-versioning.md).

For a given input, seed and set of options, and a pydicom version within the supported range:

* **Micro** releases do not change output, except for input that previously failed to anonymize. They may add support for newer Python or pydicom versions.
* **Meso** releases may modify attributes that were previously passed through, change the values generated for attributes that are not used to link objects, and drop support for old Python or pydicom versions. They do not change identifiers, UIDs, patient names or dates.
* **Macro** releases may change any output, including the values that link objects across runs.

Each release's notes list every output change by attribute, under an "Output changes" heading. Output that changes only because pydicom changes is outside this policy.

Which releases to accept depends on what you need:

| You need                                                           | Pin to (example)                                                                                                                           |
|--------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| Identical output across runs (incremental test data, golden files) | `dicognito~=0.20.0`: micro releases only. Read "Output changes" before moving to a new meso release                                        |
| Linked output across runs, but newer privacy coverage is welcome   | From 1.0, for example `dicognito>=1.4,<2`: meso and micro releases. Linking values change only in macro releases. Not available before 1.0 |
| The best privacy coverage, output reproducibility not needed       | No version constraint, and `pip install --upgrade dicognito`                                                                               |

Dependabot and Renovate read the middle number as a SemVer minor release. If you need identical output, configure them to propose meso updates separately rather than merging them automatically.

## Exactly what does dicognito do?
Using the default settings, dicognito will
* Add "DICOGNITO" to DeidentificationMethod
* Remove BranchOfService
* Remove MedicalRecordLocator
* Remove MilitaryRank
* Remove Occupation
* Remove PatientInsurancePlanCodeSequence
* Remove PatientReligiousPreference
* Remove PatientTelecomInformation
* Remove PatientTelephoneNumbers
* Remove ReferencedPatientPhotoSequence
* Remove ReferringPhysicianTelephoneNumbers
* Remove ResponsibleOrganization
* Replace AccessionNumber with anonymized values
* Replace AdmissionID with anonymized values
* Replace CountryOfResidence with anonymized values
* Replace CurrentPatientLocation with ""
* Replace FillerOrderNumberImagingServiceRequest with anonymized values
* Replace FillerOrderNumberImagingServiceRequestRetired with anonymized values
* Replace FillerOrderNumberProcedure with anonymized values
* Replace InstitutionAddress with anonymized values (unless keeping matching InstitutionName element)
* Replace InstitutionName with anonymized values
* Replace InstitutionalDepartmentName with "RADIOLOGY"
* Replace IssuerOfPatientID with "DICOGNITO"
* Replace OtherPatientIDs with anonymized values
* Replace PatientAddress with anonymized values
* Replace PatientID with anonymized values
* Replace PerformedProcedureStepID with anonymized values
* Replace PlacerOrderNumberImagingServiceRequest with anonymized values
* Replace PlacerOrderNumberImagingServiceRequestRetired with anonymized values
* Replace PlacerOrderNumberProcedure with anonymized values
* Replace ReferringPhysicianAddress with anonymized values
* Replace RegionOfResidence with anonymized values
* Replace RequestedProcedureID with anonymized values
* Replace RequestingService with ""
* Replace ScheduledProcedureStepID with anonymized values
* Replace ServiceEpisodeID with anonymized values
* Replace StationName with anonymized values
* Replace StudyID with anonymized values
* Replace all DA elements with anonymized values that precede the originals
* Replace all DT elements with anonymized values that precede the originals
* Replace all PN elements with anonymized values
* Replace all TM elements with anonymized values that precede the originals (only if replacing matching DA element)
* Replace all UI elements with anonymized values
* Replace private "MITRA LINKED ATTRIBUTES 1.0" element "Global Patient ID" with anonymized values
* Set PatientIdentityRemoved to "YES" if BurnedInAnnotation is "NO"
----
Logo: Remixed from [Radiology](https://thenounproject.com/search/?q=x-ray&i=1777366)
by [priyanka](https://thenounproject.com/creativepriyanka/) and [Incognito](https://thenounproject.com/search/?q=incognito&i=7572) by [d͡ʒɛrmi Good](https://thenounproject.com/geremygood/) from [the Noun Project](https://thenounproject.com/).
