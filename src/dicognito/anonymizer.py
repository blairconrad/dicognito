from addressanonymizer import AddressAnonymizer
from equipmentanonymizer import EquipmentAnonymizer
from fixedvalueanonymizer import FixedValueAnonymizer
from idanonymizer import IDAnonymizer
from pnanonymizer import PNAnonymizer
from datetimeanonymizer import DateTimeAnonymizer
from uianonymizer import UIAnonymizer
from unwantedelements import UnwantedElementsStripper
from randomizer import Randomizer

import random


class Anonymizer:
    def __init__(
        self,
        id_prefix="",
        id_suffix="",
        salt=None,
    ):
        minimum_offset_hours = 62 * 24
        maximum_offset_hours = 730 * 24
        randomizer = Randomizer(salt)
        address_anonymizer = AddressAnonymizer(randomizer)
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
            PNAnonymizer(randomizer),
            IDAnonymizer(
                randomizer,
                id_prefix,
                id_suffix,
                "AccessionNumber",
                "OtherPatientIDs",
                "PatientID",
                "PerformedProcedureStepID",
                "RequestedProcedureID",
                "ScheduledProcedureStepID",
                "StudyID",
            ),
            address_anonymizer,
            EquipmentAnonymizer(address_anonymizer),
            FixedValueAnonymizer("RequestingService", ""),
            FixedValueAnonymizer("CurrentPatientLocation", ""),
            DateTimeAnonymizer(-random.randint(minimum_offset_hours,
                                               maximum_offset_hours))
        ]

    def anonymize(self, dataset):
        dataset.file_meta.walk(self._anonymize_element)
        dataset.walk(self._anonymize_element)

    def _anonymize_element(self, dataset, data_element):
        for handler in self._element_handlers:
            if handler(dataset, data_element):
                return
