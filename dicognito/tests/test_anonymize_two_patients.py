import pytest

from dicognito.anonymizer import Anonymizer

from data_for_tests import load_instance


class TestTwoPatients:
    @classmethod
    def setup_class(cls):
        TestTwoPatients.dataset1 = load_instance(patient_number=1)
        TestTwoPatients.dataset2 = load_instance(patient_number=2)

        anonymizer = Anonymizer()
        anonymizer.anonymize(TestTwoPatients.dataset1)
        anonymizer.anonymize(TestTwoPatients.dataset2)

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
    def test_anonymize_all_attributes_are_different(self, element_path):
        value1 = eval("TestTwoPatients.dataset1." + element_path)
        value2 = eval("TestTwoPatients.dataset2." + element_path)
        assert value1 != value2
