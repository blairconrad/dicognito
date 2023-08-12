import pytest
from dicognito.anonymizer import Anonymizer

from .data_for_tests import load_instance


class TestTwoPatients:
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
        dataset1 = load_instance(patient_number=1)
        dataset2 = load_instance(patient_number=2)

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset1)
        anonymizer.anonymize(dataset2)

        value1 = eval("dataset1." + element_path)
        value2 = eval("dataset2." + element_path)
        assert value1 != value2

    def test_anonymize_same_patient_with_differently_formatted_name_anonymizes_the_same_way(self):
        dataset1 = load_instance(patient_number=1)
        dataset1.PatientName = "LAST^FIRST^MIDDLE"
        dataset2 = load_instance(patient_number=1)
        dataset2.PatientName = "LAST^FIRST^MIDDLE^"

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset1)
        anonymizer.anonymize(dataset2)

        value1 = dataset1.PatientName
        value2 = dataset2.PatientName
        assert value1 == value2
