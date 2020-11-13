import pytest

from dicognito.anonymizer import Anonymizer

from .data_for_tests import load_instance


class TestOneStudyTwoSerieses:
    @classmethod
    def setup_class(cls):
        TestOneStudyTwoSerieses.dataset1 = load_instance(patient_number=1, study_number=1, series_number=1)
        TestOneStudyTwoSerieses.dataset2 = load_instance(patient_number=1, study_number=1, series_number=2)

        anonymizer = Anonymizer(seed="")
        anonymizer.anonymize(TestOneStudyTwoSerieses.dataset1)
        anonymizer.anonymize(TestOneStudyTwoSerieses.dataset2)

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
            # study
            "StudyInstanceUID",
            "NameOfPhysiciansReadingStudy",
            "ReferringPhysicianName",
            "RequestingPhysician",
            "AccessionNumber",
            "StudyDate",
            "StudyID",
            "StudyTime",
        ],
    )
    def test_anonymize_patient_and_study_attributes_are_same(self, element_path):
        value1 = eval("TestOneStudyTwoSerieses.dataset1." + element_path)
        value2 = eval("TestOneStudyTwoSerieses.dataset2." + element_path)
        assert value1 == value2

    @pytest.mark.parametrize(
        "element_paths",
        [
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
            "SeriesDate,SeriesTime",
            # instance
            "SOPInstanceUID",
            "file_meta.MediaStorageSOPInstanceUID",
            "InstanceCreationDate,InstanceCreationTime",
        ],
    )
    def test_anonymize_series_and_instance_attributes_are_different(self, element_paths):
        value1 = [eval("TestOneStudyTwoSerieses.dataset1." + path) for path in element_paths.split(",")]
        value2 = [eval("TestOneStudyTwoSerieses.dataset2." + path) for path in element_paths.split(",")]
        assert value1 != value2
