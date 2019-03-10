import pytest

from dicognito.anonymizer import Anonymizer

from data_for_tests import load_instance


class TestOneStudyTwoSerieses:
    @pytest.mark.parametrize("element_path", [
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
        'NameOfPhysiciansReadingStudy',
        'ReferringPhysicianName',
        'RequestingPhysician',
        "AccessionNumber",
        "StudyDate",
        "StudyID",
        "StudyTime",
    ])
    def test_anonymize_patient_and_study_attributes_are_same(self, element_path):
        dataset1 = load_instance(
            patient_number=1, study_number=1, series_number=1)
        dataset2 = load_instance(
            patient_number=1, study_number=1, series_number=2)

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset1)
        anonymizer.anonymize(dataset2)

        value1 = eval("dataset1." + element_path)
        value2 = eval("dataset2." + element_path)
        assert value1 == value2

    @pytest.mark.parametrize("element_paths", [
        # series
        "SeriesInstanceUID",
        'OperatorsName',
        'PerformingPhysicianName',
        'RequestAttributesSequence[0].RequestedProcedureID',
        'RequestAttributesSequence[0].ScheduledProcedureStepID',
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
    ])
    def test_anonymize_series_and_instance_attributes_are_different(self, element_paths):
        dataset1 = load_instance(
            patient_number=1, study_number=1, series_number=1)
        dataset2 = load_instance(
            patient_number=1, study_number=1, series_number=2)

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset1)
        anonymizer.anonymize(dataset2)

        value1 = [eval("dataset1." + path)
                  for path in element_paths.split(",")]
        value2 = [eval("dataset2." + path)
                  for path in element_paths.split(",")]
        assert value1 != value2
