from pnanonymizer import PNAnonymizer
from idanonymizer import IDAnonymizer
from uianonymizer import UIAnonymizer


class Anonymizer:
    def __init__(self):
        self._element_handlers = [
            UIAnonymizer(),
            PNAnonymizer(),
            IDAnonymizer(
                [
                    'AccessionNumber',
                    'OtherPatientIDs',
                    'PatientID',
                    'PerformedProcedureStepID',
                    'RequestedProcedureID',
                    'ScheduledProcedureStepID',
                    'StudyID',
                ]
            )
        ]

    def anonymize(self, dataset):
        dataset.file_meta.walk(self._anonymize_element)
        dataset.walk(self._anonymize_element)

    def _anonymize_element(self, dataset, data_element):
        for handler in self._element_handlers:
            if handler(dataset, data_element):
                return
