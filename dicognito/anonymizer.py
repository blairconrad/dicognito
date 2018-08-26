from addressanonymizer import AddressAnonymizer
from idanonymizer import IDAnonymizer
from pnanonymizer import PNAnonymizer
from uianonymizer import UIAnonymizer
from unwantedelements import UnwantedElementsStripper


class Anonymizer:
    def __init__(self):
        self._element_handlers = [
            UnwantedElementsStripper(
                "BranchOfService",
                "Occupation",
                "MedicalRecordLocator",
                "MilitaryRank",
                "PatientInsurancePlanCodeSequence",
                "PatientReligiousPreference",
                "PatientTelecomInformation",
                "PatientTelephoneNumbers",
                "ReferencedPatientPhotoSequence",
                "ResponsibleOrganization",
            ),
            UIAnonymizer(),
            PNAnonymizer(),
            IDAnonymizer(
                'AccessionNumber',
                'OtherPatientIDs',
                'PatientID',
                'PerformedProcedureStepID',
                'RequestedProcedureID',
                'ScheduledProcedureStepID',
                'StudyID',
            ),
            AddressAnonymizer(),
        ]

    def anonymize(self, dataset):
        dataset.file_meta.walk(self._anonymize_element)
        dataset.walk(self._anonymize_element)

    def _anonymize_element(self, dataset, data_element):
        for handler in self._element_handlers:
            if handler(dataset, data_element):
                return
