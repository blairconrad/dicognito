"""\
Defines Anonymizer, the principle class used to anonymize DICOM objects.
"""
from dicognito.addressanonymizer import AddressAnonymizer
from dicognito.equipmentanonymizer import EquipmentAnonymizer
from dicognito.fixedvalueanonymizer import FixedValueAnonymizer
from dicognito.idanonymizer import IDAnonymizer
from dicognito.pnanonymizer import PNAnonymizer
from dicognito.datetimeanonymizer import DateTimeAnonymizer
from dicognito.uianonymizer import UIAnonymizer
from dicognito.unwantedelements import UnwantedElementsStripper
from dicognito.randomizer import Randomizer

import pydicom
import random


class Anonymizer:
    """\
    The main class responsible for anonymizing pydicom datasets.
    New instances will anonymize instances differently, so when
    anonymizing instances from the same series, study, or patient,
    reuse an Anonymizer.

    Examples
    --------
    Anonymizing a single instance:

    >>> anonymizer = Anonymizer()
    >>> with load_instance() as dataset:
    >>>     anonymizer.anonymize(dataset)
    >>>     dataset.save_as("new filename")

    Anonymizing several instances:

    >>> anonymizer = Anonymizer()
    >>> for filename in filenames:
    >>>     with load_instance(filename) as dataset:
    >>>         anonymizer.anonymize(dataset)
    >>>         dataset.save_as("new-" + filename)
    """

    def __init__(self, id_prefix="", id_suffix="", seed=None):
        """\
        Create a new Anonymizer.

        Parameters
        ----------
        id_prefix : str
            A prefix to add to all unstructured ID fields, such as Patient
            ID, Accession Number, etc.
        id_suffix : str
            A prefix to add to all unstructured ID fields, such as Patient
            ID, Accession Number, etc.
        seed
            Not intended for general use. Seeds the data randomizer in order
            to produce consistent results. Used for testing.
        """
        minimum_offset_hours = 62 * 24
        maximum_offset_hours = 730 * 24
        randomizer = Randomizer(seed)
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
        """\
        Anonymize a dataset in place. Replaces all PNs, UIs, dates and times, and
        known identifiying attributes with other vlaues.

        Parameters
        ----------
        dataset : pydicom.dataset.DataSet
            A DICOM dataset to anonymize.
        """
        dataset.file_meta.walk(self._anonymize_element)
        dataset.walk(self._anonymize_element)
        self._update_deidentification_method(dataset)
        self._update_patient_identity_removed(dataset)

    def _anonymize_element(self, dataset, data_element):
        for handler in self._element_handlers:
            if handler(dataset, data_element):
                return

    def _update_deidentification_method(self, dataset):
        if "DeidentificationMethod" not in dataset:
            dataset.DeidentificationMethod = "DICOGNITO"
            return

        existing_element = dataset.data_element("DeidentificationMethod")

        if pydicom.dataelem.isMultiValue(existing_element.value):
            if "DICOGNITO" not in existing_element.value:
                existing_element.value.append("DICOGNITO")
        elif existing_element.value != "DICOGNITO":
            existing_element.value = [existing_element.value, "DICOGNITO"]

    def _update_patient_identity_removed(self, dataset):
        if dataset.get("BurnedInAnnotation", "YES") == "NO":
            dataset.PatientIdentityRemoved = "YES"
