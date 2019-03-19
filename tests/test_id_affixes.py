import pytest

from dicognito.anonymizer import Anonymizer

from .data_for_tests import load_instance

all_id_elements = [
    "AccessionNumber",
    "OtherPatientIDs",
    "OtherPatientIDsSequence[0].PatientID",
    "PatientID",
    "PerformedProcedureStepID",
    "RequestedProcedureID",
    "ScheduledProcedureStepID",
    "StudyID",
]


@pytest.mark.parametrize("element_path", all_id_elements)
def test_id_prefix_is_prepended_to_id(element_path):
    with load_instance() as dataset:
        anonymizer = Anonymizer(id_prefix="A1")
        anonymizer.anonymize(dataset)

        actual = eval("dataset." + element_path)

        assert actual.startswith("A1")


def test_id_prefix_is_prepended_to_each_other_patient_id():
    with load_instance() as dataset:
        dataset.OtherPatientIDs = r"ID1\ID2"
        anonymizer = Anonymizer(id_prefix="B2")
        anonymizer.anonymize(dataset)

        actual = dataset.OtherPatientIDs

        assert actual[0].startswith("B2")
        assert actual[1].startswith("B2")


@pytest.mark.parametrize("element_path", all_id_elements)
def test_id_suffix_is_appended_to_id(element_path):
    with load_instance() as dataset:
        anonymizer = Anonymizer(id_suffix="1A")
        anonymizer.anonymize(dataset)

        actual = eval("dataset." + element_path)

        assert actual.endswith("1A")


def test_id_suffix_is_appended_to_each_other_patient_id():
    with load_instance() as dataset:
        dataset.OtherPatientIDs = r"ID1\ID2"
        anonymizer = Anonymizer(id_suffix="2B")
        anonymizer.anonymize(dataset)

        actual = dataset.OtherPatientIDs

        assert actual[0].endswith("2B")
        assert actual[1].endswith("2B")


def test_id_prefix_and_suffix_are_both_added_to_id():
    with load_instance() as dataset:
        anonymizer = Anonymizer(id_prefix="C3", id_suffix="3C")
        anonymizer.anonymize(dataset)

        actual = dataset.PatientID

        assert actual.startswith("C3") and actual.endswith("3C")
