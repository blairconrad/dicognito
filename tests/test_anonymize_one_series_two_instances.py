from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from dicognito.anonymizer import Anonymizer

from .data_for_tests import load_instance

if TYPE_CHECKING:
    import pydicom


class TestOneSeriesTwoInstances:
    dataset1: pydicom.dataset.Dataset
    dataset2: pydicom.dataset.Dataset

    @classmethod
    def setup_class(cls: type[TestOneSeriesTwoInstances]) -> None:
        TestOneSeriesTwoInstances.dataset1 = load_instance(
            patient_number=1,
            study_number=1,
            series_number=1,
            instance_number=1,
        )
        TestOneSeriesTwoInstances.dataset2 = load_instance(
            patient_number=1,
            study_number=1,
            series_number=1,
            instance_number=2,
        )

        anonymizer = Anonymizer(seed="")
        anonymizer.anonymize(TestOneSeriesTwoInstances.dataset1)
        anonymizer.anonymize(TestOneSeriesTwoInstances.dataset2)

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
        ],
    )
    def test_anonymize_patient_study_and_series_attributes_are_same(self, element_path):
        value1 = eval("TestOneSeriesTwoInstances.dataset1." + element_path)
        value2 = eval("TestOneSeriesTwoInstances.dataset2." + element_path)
        assert value1 == value2

    @pytest.mark.parametrize(
        "element_paths",
        [
            # instance
            "SOPInstanceUID",
            "file_meta.MediaStorageSOPInstanceUID",
            "InstanceCreationDate,InstanceCreationTime",
        ],
    )
    def test_anonymize_instance_attributes_are_different(self, element_paths):
        value1 = [eval("TestOneSeriesTwoInstances.dataset1." + path) for path in element_paths.split(",")]
        value2 = [eval("TestOneSeriesTwoInstances.dataset2." + path) for path in element_paths.split(",")]
        assert value1 != value2
