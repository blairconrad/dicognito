from __future__ import annotations

import datetime

import pydicom
import pytest
from dicognito.anonymizer import Anonymizer
from dicognito.pnanonymizer import PNAnonymizer

from .data_for_tests import load_dcm, load_minimal_instance, load_test_instance


def test_minimal_instance_anonymizes_safely():
    with load_minimal_instance() as dataset:
        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)


@pytest.mark.parametrize(
    "element_path",
    [
        "file_meta.MediaStorageSOPClassUID",
        "file_meta.TransferSyntaxUID",
        "file_meta.ImplementationClassUID",
        "SOPClassUID",
        "SourceImageSequence[0].ReferencedSOPClassUID",
    ],
)
def test_nonidentifying_uis_are_left_alone(element_path):
    with load_test_instance() as dataset:
        expected = eval("dataset." + element_path)

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        actual = eval("dataset." + element_path)

        assert actual == expected


@pytest.mark.parametrize(
    "element_path",
    [
        "file_meta.MediaStorageSOPInstanceUID",
        "SOPInstanceUID",
        "SourceImageSequence[0].ReferencedSOPInstanceUID",
        "StudyInstanceUID",
        "SeriesInstanceUID",
        "FrameOfReferenceUID",
    ],
)
def test_identifying_uis_are_updated(element_path):
    with load_test_instance() as dataset:
        expected = eval("dataset." + element_path)

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        actual = eval("dataset." + element_path)

        assert actual != expected


@pytest.mark.parametrize(
    ("one_element_path", "another_element_path"),
    [("file_meta.MediaStorageSOPInstanceUID", "SOPInstanceUID")],
)
def test_repeated_identifying_uis_get_same_values(one_element_path, another_element_path):
    with load_test_instance() as dataset:
        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        one_uid = eval("dataset." + one_element_path)
        another_uid = eval("dataset." + another_element_path)

        assert one_uid == another_uid


@pytest.mark.parametrize(
    "element_path",
    [
        "AccessionNumber",
        "FillerOrderNumberImagingServiceRequest",
        "FillerOrderNumberImagingServiceRequestRetired",
        "FillerOrderNumberProcedure",
        "IssuerOfPatientID",
        "OtherPatientIDs",
        "OtherPatientIDsSequence[0].PatientID",
        "OtherPatientIDsSequence[0].IssuerOfPatientID",
        "OtherPatientIDsSequence[1].PatientID",
        "OtherPatientIDsSequence[1].IssuerOfPatientID",
        "PatientID",
        "PerformedProcedureStepID",
        "PlacerOrderNumberImagingServiceRequest",
        "PlacerOrderNumberImagingServiceRequestRetired",
        "PlacerOrderNumberProcedure",
        "RequestAttributesSequence[0].RequestedProcedureID",
        "RequestAttributesSequence[0].ScheduledProcedureStepID",
        "ScheduledProcedureStepID",
        "StudyID",
    ],
)
def test_ids_are_anonymized(element_path):
    with load_test_instance() as dataset:
        original = eval("dataset." + element_path)
        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        actual = eval("dataset." + element_path)

        assert actual != original


def test_single_other_patient_ids_anonymized_to_single_id():
    with load_test_instance() as dataset:
        dataset.OtherPatientIDs = ["ID1"]

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        actual: str = dataset.OtherPatientIDs  # type: ignore[assignment]

        assert actual != "ID1"
        assert isinstance(actual, str)


@pytest.mark.parametrize("number_of_ids", [2, 3])
def test_other_patient_ids_anonymized_to_same_number_of_ids(number_of_ids):
    with load_test_instance() as dataset:
        original = ["ID" + str(i) for i in range(1, number_of_ids + 1)]
        dataset.OtherPatientIDs = original

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        actual = dataset.OtherPatientIDs

        assert len(actual) == number_of_ids
        for actual_id, original_id in zip(actual, original):
            assert isinstance(actual_id, str)
            assert actual_id != original_id


def test_issuer_of_patient_id_changed_if_not_empty():
    with load_test_instance() as dataset:
        dataset.IssuerOfPatientID = "NOTEMPTY"

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        actual = dataset.IssuerOfPatientID

        assert actual == "DICOGNITO"


def test_issuer_of_patient_id_not_added_if_empty():
    with load_test_instance() as dataset:
        dataset.IssuerOfPatientID = ""

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        actual = dataset.IssuerOfPatientID

        assert actual == ""


def test_female_patient_name_gets_anonymized():
    with load_test_instance() as dataset:
        dataset.PatientSex = "F"
        dataset.PatientName = pydicom.valuerep.PersonName("LAST^FIRST^MIDDLE")

        original_patient_name = dataset.PatientName

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        new_patient_name = dataset.PatientName

        assert new_patient_name != original_patient_name
        assert new_patient_name.family_name in PNAnonymizer._last_names
        assert new_patient_name.given_name in PNAnonymizer._female_first_names
        assert new_patient_name.middle_name in PNAnonymizer._all_first_names


def test_male_patient_name_gets_anonymized():
    with load_test_instance() as dataset:
        dataset.PatientSex = "M"
        dataset.PatientName = pydicom.valuerep.PersonName("LAST^FIRST^MIDDLE")

        original_patient_name = dataset.PatientName

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        new_patient_name = dataset.PatientName

        assert new_patient_name != original_patient_name
        assert new_patient_name.family_name in PNAnonymizer._last_names
        assert new_patient_name.given_name in PNAnonymizer._male_first_names
        assert new_patient_name.middle_name in PNAnonymizer._all_first_names


def test_sex_other_patient_name_gets_anonymized():
    with load_test_instance() as dataset:
        dataset.PatientSex = "O"
        dataset.PatientName = pydicom.valuerep.PersonName("LAST^FIRST^MIDDLE")

        original_patient_name = dataset.PatientName

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        new_patient_name = dataset.PatientName

        assert new_patient_name != original_patient_name
        assert new_patient_name.family_name in PNAnonymizer._last_names
        assert new_patient_name.given_name in PNAnonymizer._all_first_names
        assert new_patient_name.middle_name in PNAnonymizer._all_first_names


def test_single_other_patient_names_anonymized_to_single_name():
    with load_test_instance() as dataset:
        original = ["NAME1"]
        dataset.OtherPatientNames = original

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        actual = dataset.OtherPatientNames

        assert actual != original
        assert type(actual) is pydicom.valuerep.PersonName  # type: ignore[comparison-overlap, unreachable]


@pytest.mark.parametrize("number_of_names", [2, 3])
def test_other_patient_names_anonymized_to_same_number_of_names(number_of_names):
    with load_test_instance() as dataset:
        original = ["NAME" + str(i) for i in range(1, number_of_names + 1)]
        dataset.OtherPatientNames = original

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        actual = dataset.OtherPatientNames

        assert actual != original
        assert len(set(actual)) == number_of_names


@pytest.mark.parametrize(
    "element_path",
    [
        "NameOfPhysiciansReadingStudy",
        "OperatorsName",
        "PatientBirthName",
        "PatientMotherBirthName",
        "PerformingPhysicianName",
        "ReferringPhysicianName",
        "RequestingPhysician",
        "ResponsiblePerson",
    ],
)
def test_non_patient_names_get_anonymized(element_path):
    with load_test_instance() as dataset:
        original_name = eval("dataset." + element_path)
        assert original_name

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        new_name = eval("dataset." + element_path)
        assert new_name != original_name


def test_patient_address_gets_anonymized():
    with load_test_instance() as dataset:
        original_address = dataset.PatientAddress
        original_region = dataset.RegionOfResidence
        original_country = dataset.CountryOfResidence

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        new_address = dataset.PatientAddress
        new_region = dataset.RegionOfResidence
        new_country = dataset.CountryOfResidence

        assert new_address != original_address
        assert new_region != original_region
        assert new_country != original_country


@pytest.mark.parametrize(
    "element_name",
    [
        "Occupation",
        "PatientInsurancePlanCodeSequence",
        "MilitaryRank",
        "BranchOfService",
        "PatientTelephoneNumbers",
        "PatientTelecomInformation",
        "PatientReligiousPreference",
        "MedicalRecordLocator",
        "ReferencedPatientPhotoSequence",
        "ResponsibleOrganization",
    ],
)
def test_extra_patient_attributes_are_removed(element_name):
    with load_test_instance() as dataset:
        assert element_name in dataset

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        assert element_name not in dataset


def test_equipment_gets_anonymized():
    with load_test_instance() as dataset:
        original_institution_name = dataset.InstitutionName
        original_institution_address = dataset.InstitutionAddress
        original_institutional_department_name = dataset.InstitutionalDepartmentName
        original_station_name = dataset.StationName

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        new_institution_name = dataset.InstitutionName
        new_institution_address = dataset.InstitutionAddress
        new_institutional_department_name = dataset.InstitutionalDepartmentName
        new_station_name = dataset.StationName

        assert new_institution_name != original_institution_name
        assert new_institution_address != original_institution_address
        assert new_institutional_department_name != original_institutional_department_name
        assert new_station_name != original_station_name


def test_station_gets_anonymized_when_no_modality():
    with load_test_instance() as dataset:
        original_station_name = dataset.StationName
        del dataset.Modality

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        new_station_name = dataset.StationName

        assert new_station_name != original_station_name


def test_requesting_service_gets_anonymized():
    with load_test_instance() as dataset:
        original = dataset.RequestingService

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        actual = dataset.RequestingService

        assert actual != original


def test_current_patient_location_gets_anonymized():
    with load_test_instance() as dataset:
        original = dataset.CurrentPatientLocation

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        actual = dataset.CurrentPatientLocation

        assert actual != original


@pytest.mark.parametrize(
    "date_name",
    [
        "AcquisitionDate",
        "ContentDate",
        "InstanceCreationDate",
        "PatientBirthDate",
        "PerformedProcedureStepStartDate",
        "SeriesDate",
        "StudyDate",
    ],
)
def test_dates_and_times_get_anonymized_when_both_are_present(date_name):
    time_name = date_name[:-4] + "Time"

    original_datetime = datetime.datetime(1974, 11, 3, 12, 15, 58)  # noqa: DTZ001
    original_date_string = original_datetime.strftime("%Y%m%d")
    original_time_string = original_datetime.strftime("%H%M%S")

    with load_test_instance() as dataset:
        setattr(dataset, date_name, original_date_string)
        setattr(dataset, time_name, original_time_string)

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        new_date_string = getattr(dataset, date_name)
        new_time_string = getattr(dataset, time_name)

    assert (new_date_string, new_time_string) != (original_date_string, original_time_string)


def test_date_gets_anonymized_when_there_is_no_time():
    with load_test_instance() as dataset:
        original_birth_date = dataset.PatientBirthDate = "19830213"
        assert "PatientBirthTime" not in dataset

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        new_birth_date = dataset.PatientBirthDate

    assert new_birth_date != original_birth_date
    assert "PatientBirthTime" not in dataset


def test_date_gets_anonymized_when_time_is_present():
    dataset = load_test_instance()
    dataset.PatientBirthDate = original_birth_date = "20180202"
    dataset.PatientBirthTime = original_birth_time = "123456"

    anonymizer = Anonymizer()
    anonymizer.anonymize(dataset)

    new_date_string = dataset.PatientBirthDate
    new_time_string = dataset.PatientBirthTime

    assert new_date_string != original_birth_date
    assert len(new_date_string) == len(original_birth_date)
    assert new_time_string[2:] == original_birth_time[2:]
    assert len(new_time_string) == len(original_birth_time)


@pytest.mark.parametrize(
    "birth_time",
    ["", "07", "0911", "131517", "192123.1", "192123.12", "192123.123", "192123.1234", "192123.12345", "192123.123456"],
)
def test_date_gets_anonymized_when_time_has_various_lengths(birth_time):
    with load_test_instance() as dataset:
        dataset.PatientBirthDate = original_birth_date = "20010401"
        dataset.PatientBirthTime = birth_time

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        new_date_string = dataset.PatientBirthDate
        new_time_string = dataset.PatientBirthTime

    assert new_date_string != original_birth_date
    assert len(new_date_string) == len(original_birth_date)
    assert new_time_string[2:] == birth_time[2:]
    assert len(new_time_string) == len(birth_time)


def test_multivalued_date_with_no_time_pair_gets_anonymized():
    with load_test_instance() as dataset:
        dataset.DateOfLastCalibration = original_date = ["20010401", "20010402"]

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        new_date_string = dataset.DateOfLastCalibration

    assert new_date_string != original_date
    assert len(new_date_string) == len(original_date)


def test_multivalued_date_and_time_pair_gets_anonymized():
    with load_test_instance() as dataset:
        dataset.DateOfLastCalibration = original_date = ["20010401", "20010402"]
        dataset.TimeOfLastCalibration = original_time = ["120000", "135959"]

        anonymizer = Anonymizer(seed="")
        anonymizer.anonymize(dataset)

        new_date = dataset.DateOfLastCalibration
        new_time = dataset.TimeOfLastCalibration

    assert new_date != original_date
    assert len(new_date) == len(original_date)
    assert new_time != original_time
    assert len(new_time) == len(original_time)


def test_multivalued_date_and_time_pair_gets_anonymized_same_with_same_seed():
    with load_test_instance() as dataset1, load_test_instance() as dataset2:
        dataset1.DateOfLastCalibration = original_date = ["20010401", "20010402"]
        dataset1.TimeOfLastCalibration = original_time = ["120000", "135959"]
        dataset2.DateOfLastCalibration = original_date
        dataset2.TimeOfLastCalibration = original_time

        Anonymizer(seed="").anonymize(dataset1)
        Anonymizer(seed="").anonymize(dataset2)

        new_date1 = dataset1.DateOfLastCalibration
        new_time1 = dataset1.TimeOfLastCalibration
        new_date2 = dataset2.DateOfLastCalibration
        new_time2 = dataset2.TimeOfLastCalibration

    assert new_date1 == new_date2
    assert new_time1 == new_time2


def test_issue_date_of_imaging_service_request_gets_anonymized():
    original_datetime = datetime.datetime(1974, 11, 3, 12, 15, 58)  # noqa: DTZ001
    original_date_string = original_datetime.strftime("%Y%m%d")
    original_time_string = original_datetime.strftime("%H%M%S")

    with load_test_instance() as dataset:
        dataset.IssueDateOfImagingServiceRequest = original_date_string
        dataset.IssueTimeOfImagingServiceRequest = original_time_string

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        new_date_string = dataset.IssueDateOfImagingServiceRequest
        new_time_string = dataset.IssueTimeOfImagingServiceRequest
    assert (new_date_string, new_time_string) != (original_date_string, original_time_string)


@pytest.mark.parametrize(
    "datetime_name",
    [
        "AcquisitionDateTime",
        "FrameReferenceDateTime",
        "FrameAcquisitionDateTime",
        "StartAcquisitionDateTime",
        "EndAcquisitionDateTime",
        "PerformedProcedureStepStartDateTime",
        "PerformedProcedureStepEndDateTime",
    ],
)
def test_datetime_gets_anonymized(datetime_name):
    original_datetime = datetime.datetime(1974, 11, 3, 12, 15, 58)  # noqa: DTZ001
    original_datetime_string = original_datetime.strftime("%Y%m%d%H%M%S")

    with load_test_instance() as dataset:
        setattr(dataset, datetime_name, original_datetime_string)

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        new_datetime_string = getattr(dataset, datetime_name)

    assert new_datetime_string != original_datetime_string


@pytest.mark.parametrize(
    "acquisition_datetime",
    [
        "1947",
        "194711",
        "19471103",
        "1947110307",
        "194711030911",
        "19471103131517",
        "19471103192123.1",
        "19471103192123.12",
        "19471103192123.123",
        "19471103192123.1234",
        "19471103192123.12345",
        "19471103192123.123456",
    ],
)
def test_datetime_of_various_lengths_gets_anonymized(acquisition_datetime):
    with load_test_instance() as dataset:
        dataset.AcquisitionDateTime = acquisition_datetime

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        new_datetime_string = dataset.AcquisitionDateTime

    assert new_datetime_string != acquisition_datetime
    assert len(new_datetime_string) == len(acquisition_datetime)


def test_multivalued_datetime_gets_anonymized():
    with load_test_instance() as dataset:
        dataset.AcquisitionDateTime = original_datetime = ["19741103121558", "19721004161558"]

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        new_datetime = dataset.AcquisitionDateTime

    assert new_datetime != original_datetime
    assert len(new_datetime) == len(original_datetime)


def test_no_sex_still_changes_patient_name():
    with load_test_instance() as dataset:
        del dataset.PatientSex

        original_patient_name = dataset.PatientName

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        new_patient_name = dataset.PatientName

    assert new_patient_name != original_patient_name


@pytest.mark.parametrize(
    ("initial", "expected"),
    [
        (None, "DICOGNITO"),
        ("DICOGNITO", "DICOGNITO"),
        ("SOMETHINGELSE", ["SOMETHINGELSE", "DICOGNITO"]),
        (r"SOMETHING\SOMETHINGELSE", ["SOMETHING", "SOMETHINGELSE", "DICOGNITO"]),
        (r"DICOGNITO\SOMETHINGELSE", ["DICOGNITO", "SOMETHINGELSE"]),
    ],
)
def test_deidentification_method_set_properly(initial, expected):
    with load_test_instance() as dataset:
        ensure_attribute_is(dataset, "DeidentificationMethod", initial)

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        assert_attribute_is(dataset, "DeidentificationMethod", expected)


@pytest.mark.parametrize(
    ("initial_patient_identity_removed", "burned_in_annotation", "expected_patient_identity_removed"),
    [
        (None, None, None),
        (None, "YES", None),
        (None, "NO", "YES"),
        ("NO", None, "NO"),
        ("NO", "YES", "NO"),
        ("NO", "NO", "YES"),
        ("YES", None, "YES"),
        ("YES", "YES", "YES"),
        ("YES", "NO", "YES"),
    ],
)
def test_patient_identity_removed(
    initial_patient_identity_removed,
    burned_in_annotation,
    expected_patient_identity_removed,
):
    with load_test_instance() as dataset:
        ensure_attribute_is(dataset, "PatientIdentityRemoved", initial_patient_identity_removed)
        ensure_attribute_is(dataset, "BurnedInAnnotation", burned_in_annotation)

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        assert_attribute_is(dataset, "PatientIdentityRemoved", expected_patient_identity_removed)


def test_pixel_data_with_embedded_sequence_delimiter():
    with load_dcm(
        "orig_data",
        "test_pixel_data_with_embedded_sequence_delimiter",
        "JPEG2000-embedded-sequence-delimiter.dcm",
    ) as dataset:
        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)


def ensure_attribute_is(dataset: pydicom.dataset.Dataset, attribute_name: str, value: str | None) -> None:
    if value is None:
        assert attribute_name not in dataset
    else:
        setattr(dataset, attribute_name, value)


def assert_attribute_is(dataset: pydicom.dataset.Dataset, attribute_name: str, expected: str | None) -> None:
    if expected is None:
        assert attribute_name not in dataset
    else:
        assert expected == getattr(dataset, attribute_name)
