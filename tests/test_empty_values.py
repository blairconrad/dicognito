import re

import pydicom
import pytest
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.sequence import Sequence

from dicognito.anonymizer import Anonymizer

REMOVED_KEYWORDS = [
    "BranchOfService",
    "MedicalRecordLocator",
    "MilitaryRank",
    "Occupation",
    "PatientReligiousPreference",
    "PatientTelecomInformation",
    "PatientTelephoneNumbers",
    "ReferringPhysicianTelephoneNumbers",
    "ResponsibleOrganization",
]
REMOVED_SEQUENCE_KEYWORDS = ["PatientInsurancePlanCodeSequence", "ReferencedPatientPhotoSequence"]

UID_KEYWORDS = ["StudyInstanceUID", "ReferencedSOPInstanceUID"]
PERSON_NAME_KEYWORDS = ["PatientName", "ReferringPhysicianName", "OtherPatientNames"]
ID_KEYWORDS = [
    "AccessionNumber",
    "AdmissionID",
    "OtherPatientIDs",
    "FillerOrderNumberImagingServiceRequest",
    "FillerOrderNumberImagingServiceRequestRetired",
    "FillerOrderNumberProcedure",
    "PatientID",
    "PerformedProcedureStepID",
    "PlacerOrderNumberImagingServiceRequest",
    "PlacerOrderNumberImagingServiceRequestRetired",
    "PlacerOrderNumberProcedure",
    "RequestedProcedureID",
    "ScheduledProcedureStepID",
    "ServiceEpisodeID",
    "StationName",
    "StudyID",
]
ISSUER_KEYWORDS = ["IssuerOfPatientID"]
ADDRESS_KEYWORDS = [
    "PatientAddress",
    "RegionOfResidence",
    "CountryOfResidence",
    "ReferringPhysicianAddress",
    "InstitutionAddress",
]
INSTITUTION_KEYWORDS = ["InstitutionName", "InstitutionalDepartmentName"]
FIXED_VALUE_KEYWORDS = ["RequestingService", "CurrentPatientLocation"]
DATE_TIME_KEYWORDS = ["StudyDate", "AcquisitionDateTime", "StudyTime"]

SCALAR_KEYWORDS = [
    *UID_KEYWORDS,
    *PERSON_NAME_KEYWORDS,
    *ID_KEYWORDS,
    *ISSUER_KEYWORDS,
    *ADDRESS_KEYWORDS,
    *INSTITUTION_KEYWORDS,
    *FIXED_VALUE_KEYWORDS,
    *DATE_TIME_KEYWORDS,
]

EMPTY_VALUES = {"empty string": "", "None": None, "empty bytes": b""}

# keyword -> a non-empty component to put after an empty one
COMPONENT_KEYWORDS = {
    "SOPClassesInStudy": "1.2.3",
    "OtherPatientNames": "DOE^JANE",
    "PerformingPhysicianName": "DOE^JOHN",
    "OtherPatientIDs": "A1",
    "DateOfLastCalibration": "20200102",
    "DateTimeOfLastCalibration": "20200102101010",
}

KnownDefect = tuple[str, type[Exception]]

# Each known defect is a reason and the exception type the test fails with today.
# Marking the type keeps a test from passing as an xfail for some unrelated reason.
POPULATED_BY_ID = ("empty IDs are replaced with a generated ID", AssertionError)
RAISED_BY_ID = ("an ID with a None or empty-bytes value raises", TypeError)
POPULATED_BY_INSTITUTION = ("#194 empty institution values are replaced with generated ones", AssertionError)
RAISED_BY_INSTITUTION_NAME = ("an InstitutionName with a None or empty-bytes value raises", TypeError)
RAISED_BY_PERSON_NAME_COMPONENT = ("an empty component of a multi-valued PN raises", TypeError)
RAISED_BY_DATE_COMPONENT = ("an empty component of a multi-valued DA or DT raises", ValueError)
POPULATED_BY_UID_COMPONENT = ("an empty component of a multi-valued UI is replaced with a UID", AssertionError)


def known_defect_for_scalar(keyword: str, empty_name: str) -> KnownDefect | None:
    if keyword in ID_KEYWORDS:
        return POPULATED_BY_ID if empty_name == "empty string" else RAISED_BY_ID
    if keyword == "InstitutionName":
        return POPULATED_BY_INSTITUTION if empty_name == "empty string" else RAISED_BY_INSTITUTION_NAME
    if keyword == "InstitutionalDepartmentName":
        return POPULATED_BY_INSTITUTION
    return None


def known_defect_for_component(keyword: str) -> KnownDefect | None:
    value_representation = pydicom.datadict.dictionary_VR(keyword)
    return {
        "PN": RAISED_BY_PERSON_NAME_COMPONENT,
        "DA": RAISED_BY_DATE_COMPONENT,
        "DT": RAISED_BY_DATE_COMPONENT,
        "LO": POPULATED_BY_ID,
        "UI": POPULATED_BY_UID_COMPONENT,
    }.get(value_representation)


def mark_known_defect(known_defect: KnownDefect | None) -> list[pytest.MarkDecorator]:
    if known_defect is None:
        return []
    reason, exception_type = known_defect
    return [pytest.mark.xfail(strict=True, raises=exception_type, reason=reason)]


@pytest.mark.parametrize("keyword", REMOVED_KEYWORDS)
@pytest.mark.parametrize("empty_name", EMPTY_VALUES)
def test_unwanted_element_with_empty_value_is_removed(keyword, empty_name):
    dataset = anonymize_one_element(keyword, EMPTY_VALUES[empty_name])

    assert keyword not in dataset


@pytest.mark.parametrize(
    ("keyword", "empty_name"),
    [
        pytest.param(keyword, empty_name, marks=mark_known_defect(known_defect_for_scalar(keyword, empty_name)))
        for keyword in SCALAR_KEYWORDS
        for empty_name in EMPTY_VALUES
    ],
)
def test_empty_value_stays_empty(keyword, empty_name):
    dataset = anonymize_one_element(keyword, EMPTY_VALUES[empty_name])

    assert keyword in dataset
    assert not dataset[keyword].value


@pytest.mark.parametrize(
    "keyword",
    [
        pytest.param(keyword, marks=mark_known_defect(known_defect_for_component(keyword)))
        for keyword in COMPONENT_KEYWORDS
    ],
)
def test_empty_component_of_multi_valued_element_stays_empty(keyword):
    original_value = COMPONENT_KEYWORDS[keyword]

    dataset = anonymize_one_element(keyword, ["", original_value])

    anonymized_values = list(dataset[keyword].value)
    assert len(anonymized_values) == 2  # noqa: PLR2004
    assert not anonymized_values[0]
    assert anonymized_values[1] != original_value


@pytest.mark.parametrize("keyword", REMOVED_SEQUENCE_KEYWORDS)
def test_empty_sequence_of_unwanted_element_is_removed(keyword):
    dataset = anonymize_one_element(keyword, Sequence([]))

    assert keyword not in dataset


def test_empty_sequence_is_kept():
    dataset = anonymize_one_element("ReferencedStudySequence", Sequence([]))

    assert "ReferencedStudySequence" in dataset
    assert len(dataset.ReferencedStudySequence) == 0


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="empty accession numbers are replaced with one shared generated value",
)
def test_empty_accession_numbers_in_different_objects_stay_empty():
    anonymizer = Anonymizer(seed="empty values")
    anonymized_accession_numbers = []

    for study_instance_uid in ("1.2.3.1", "1.2.3.2"):
        dataset = Dataset()
        dataset.file_meta = FileMetaDataset()
        dataset.StudyInstanceUID = study_instance_uid
        dataset.AccessionNumber = ""
        anonymizer.anonymize(dataset)
        anonymized_accession_numbers.append(dataset.AccessionNumber)

    assert anonymized_accession_numbers == ["", ""]


def test_every_keyword_the_anonymizer_acts_on_is_tested_for_empty_values():
    described_keywords = {
        match.group(1)
        for match in re.finditer(r"^\* (?:Remove|Replace) (\w+)", Anonymizer().describe_actions(), re.MULTILINE)
        if pydicom.datadict.tag_for_keyword(match.group(1)) is not None
    }
    tested_keywords = {
        *REMOVED_KEYWORDS,
        *REMOVED_SEQUENCE_KEYWORDS,
        *ID_KEYWORDS,
        *ISSUER_KEYWORDS,
        *ADDRESS_KEYWORDS,
        *INSTITUTION_KEYWORDS,
        *FIXED_VALUE_KEYWORDS,
    }

    assert tested_keywords == described_keywords


def anonymize_one_element(keyword: str, value: object) -> Dataset:
    dataset = Dataset()
    dataset.file_meta = FileMetaDataset()
    setattr(dataset, keyword, value)
    Anonymizer(seed="empty values").anonymize(dataset)
    return dataset
