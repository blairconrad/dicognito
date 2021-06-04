import pydicom
import pytest

from dicognito.anonymizer import Anonymizer

from .data_for_tests import load_instance


class TestOnePatientTwoStudies:
    dataset1: pydicom.dataset.Dataset
    dataset2: pydicom.dataset.Dataset

    @classmethod
    def setup_class(cls):
        TestOnePatientTwoStudies.dataset1 = load_instance(patient_number=1, study_number=1)
        TestOnePatientTwoStudies.dataset2 = load_instance(patient_number=1, study_number=2)

        anonymizer = Anonymizer(seed="")
        anonymizer.anonymize(TestOnePatientTwoStudies.dataset1)
        anonymizer.anonymize(TestOnePatientTwoStudies.dataset2)

    @pytest.mark.parametrize(
        "element_path",
        [
            # patient
            "PatientID",
            "OtherPatientIDs",
            "OtherPatientIDsSequence[0].PatientID",
            "OtherPatientNames",
            "PatientAddress",
            "PatientBirthDate",
            "PatientBirthName",
            "PatientBirthTime",
            "PatientMotherBirthName",
            "PatientName",
            "ResponsiblePerson",
        ],
    )
    def test_anonymize_patient_attributes_are_same(self, element_path):
        value1 = eval("TestOnePatientTwoStudies.dataset1." + element_path)
        value2 = eval("TestOnePatientTwoStudies.dataset2." + element_path)
        assert value1 == value2

    @pytest.mark.parametrize(
        "element_path",
        [
            # study
            "StudyInstanceUID",
            "NameOfPhysiciansReadingStudy",
            "ReferringPhysicianName",
            "RequestingPhysician",
            "AccessionNumber",
            "StudyDate",
            "StudyID",
            "StudyTime",
            # series
            "SeriesInstanceUID",
            "OperatorsName",
            "PerformingPhysicianName",
            "RequestAttributesSequence[0].RequestedProcedureID",
            "RequestAttributesSequence[0].ScheduledProcedureStepID",
            "FrameOfReferenceUID",
            "InstitutionAddress",
            "InstitutionName",
            "PerformedProcedureStepID",
            "RequestedProcedureID",
            "ScheduledProcedureStepID",
            "SeriesDate",
            "SeriesTime",
            # instance
            "SOPInstanceUID",
            "file_meta.MediaStorageSOPInstanceUID",
            "InstanceCreationDate",
            "InstanceCreationTime",
        ],
    )
    def test_anonymize_study_series_and_instance_attributes_are_different(self, element_path):
        value1 = eval("TestOnePatientTwoStudies.dataset1." + element_path)
        value2 = eval("TestOnePatientTwoStudies.dataset2." + element_path)
        assert value1 != value2
