from dicognito.addressanonymizer import AddressAnonymizer
from dicognito.equipmentanonymizer import EquipmentAnonymizer
from dicognito.fixedvalueanonymizer import FixedValueAnonymizer
from dicognito.idanonymizer import IDAnonymizer
from dicognito.pnanonymizer import PNAnonymizer
from dicognito.datetimeanonymizer import DateTimeAnonymizer
from dicognito.uianonymizer import UIAnonymizer
from dicognito.unwantedelements import UnwantedElementsStripper
from dicognito.randomizer import Randomizer

import random


class Anonymizer:
    def __init__(self, id_prefix="", id_suffix="", salt=None):
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
            DateTimeAnonymizer(-random.randint(minimum_offset_hours, maximum_offset_hours)),
        ]

    def anonymize(self, dataset):
        dataset.file_meta.walk(self._anonymize_element)
        dataset.walk(self._anonymize_element)

    def _anonymize_element(self, dataset, data_element):
        for handler in self._element_handlers:
            if handler(dataset, data_element):
                return
