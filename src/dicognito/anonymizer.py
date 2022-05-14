"""\
Defines Anonymizer, the principle class used to anonymize DICOM objects.
"""
from typing import Callable, Optional, Sequence
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

    def __init__(self, id_prefix: str = "", id_suffix: str = "", seed: Optional[str] = None) -> None:
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
        seed : Optional[str]
            Seeds the data randomizer, which will produce consistent results when
            invoked with the same seed.
        """
        minimum_offset_hours = 62 * 24
        maximum_offset_hours = 730 * 24

        randomizer = Randomizer(seed)

        date_offset_hours = -(
            randomizer.to_int("date_offset") % (maximum_offset_hours - minimum_offset_hours) + minimum_offset_hours
        )
        address_anonymizer = AddressAnonymizer(randomizer)

        self._element_handlers: Sequence[Callable[[pydicom.dataset.Dataset, pydicom.dataelem.DataElement], bool]] = [
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
            UIAnonymizer(randomizer),
            PNAnonymizer(randomizer),
            IDAnonymizer(
                randomizer,
                id_prefix,
                id_suffix,
                "AccessionNumber",
                "OtherPatientIDs",
                "FillerOrderNumberImagingServiceRequest",
                "FillerOrderNumberImagingServiceRequestRetired",
                "FillerOrderNumberProcedure",
                "PatientID",
                "PerformedProcedureStepID",
                "PlacerOrderNumberImagingServiceRequest",
                "PlacerOrderNumberImagingServiceRequestRetired",
                "PlacerOrderNumberProcedure",
                "RequestedProcedureID",
                "ScheduledProcedureStepID",
                "StationName",
                "StudyID",
            ),
            address_anonymizer,
            EquipmentAnonymizer(address_anonymizer),
            FixedValueAnonymizer("RequestingService", ""),
            FixedValueAnonymizer("CurrentPatientLocation", ""),
            DateTimeAnonymizer(date_offset_hours),
        ]

    def anonymize(self, dataset: pydicom.dataset.Dataset) -> None:
        """\
        Anonymize a dataset in place. Replaces all PNs, UIs, dates and times, and
        known identifiying attributes with other vlaues.

        Parameters
        ----------
        dataset : pydicom.dataset.Dataset
            A DICOM dataset to anonymize.
        """
        dataset.file_meta.walk(self._anonymize_element)
        dataset.walk(self._anonymize_element)
        self._update_deidentification_method(dataset)
        self._update_patient_identity_removed(dataset)

    def _anonymize_element(self, dataset: pydicom.dataset.Dataset, data_element: pydicom.dataelem.DataElement) -> None:
        for handler in self._element_handlers:
            if handler(dataset, data_element):
                return

    def _update_deidentification_method(self, dataset: pydicom.dataset.Dataset) -> None:
        if "DeidentificationMethod" not in dataset:
            dataset.DeidentificationMethod = "DICOGNITO"
            return

        existing_element = dataset.data_element("DeidentificationMethod")
        assert existing_element is not None  # satisfy mypy
        existing_value = existing_element.value

        if isinstance(existing_value, pydicom.multival.MultiValue):
            if "DICOGNITO" not in existing_value:
                existing_value.append("DICOGNITO")
        elif existing_value != "DICOGNITO":
            existing_element.value = [existing_value, "DICOGNITO"]

    def _update_patient_identity_removed(self, dataset: pydicom.dataset.Dataset) -> None:
        if dataset.get("BurnedInAnnotation", "YES") == "NO":
            dataset.PatientIdentityRemoved = "YES"
