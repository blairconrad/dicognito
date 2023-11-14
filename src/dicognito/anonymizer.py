"""Defines Anonymizer, the principle class used to anonymize DICOM objects."""
from __future__ import annotations

from typing import TYPE_CHECKING, Iterator, MutableSequence, Sequence

from dicognito.addressanonymizer import AddressAnonymizer
from dicognito.dataset_updater import DatasetUpdater, DeidentificationMethodUpdater, PatientIdentityRemovedUpdater
from dicognito.datetimeanonymizer import DateTimeAnonymizer
from dicognito.equipmentanonymizer import EquipmentAnonymizer
from dicognito.fixedvalueanonymizer import FixedValueAnonymizer
from dicognito.idanonymizer import IDAnonymizer
from dicognito.pnanonymizer import PNAnonymizer
from dicognito.randomizer import Randomizer
from dicognito.uianonymizer import UIAnonymizer
from dicognito.unwantedelements import UnwantedElementsStripper

if TYPE_CHECKING:
    import pydicom

    from dicognito.element_anonymizer import ElementAnonymizer


class Anonymizer:
    """
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

    def __init__(self, id_prefix: str = "", id_suffix: str = "", seed: str | None = None) -> None:
        """
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

        self._element_handlers: MutableSequence[ElementAnonymizer] = [
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

        self._dataset_updaters: Sequence[DatasetUpdater] = [
            DeidentificationMethodUpdater(),
            PatientIdentityRemovedUpdater(),
        ]

    def anonymize(self, dataset: pydicom.dataset.Dataset) -> None:
        """
        Anonymize a dataset in place.

        Replaces all PNs, UIs, dates and times, and
        known identifying elements with other values.

        Parameters
        ----------
        dataset : pydicom.dataset.Dataset
            A DICOM dataset to anonymize.
        """
        dataset.file_meta.walk(self._anonymize_element)
        dataset.walk(self._anonymize_element)
        for updater in self._dataset_updaters:
            updater(dataset)

    def describe_actions(self) -> str:
        """Describe all the actions this anonymizer performs."""

        def actions() -> Iterator[str]:
            for handler in self._element_handlers:
                yield from handler.describe_actions()
            for updater in self._dataset_updaters:
                yield from updater.describe_actions()

        return "* " + "\n* ".join(sorted(actions()))

    def add_element_handler(self, handler: ElementAnonymizer) -> None:
        """
        Add a new element handler to the beginning of registered handlers.

        The new handler will be invoked before any previously-added (or default) handlers.

        Parameters
        ----------
        handler : dicognito.element_anonymizer.ElementAnonymizer
            The new element handler.
        """
        self._element_handlers.insert(0, handler)

    def _anonymize_element(self, dataset: pydicom.dataset.Dataset, data_element: pydicom.dataelem.DataElement) -> None:
        for handler in self._element_handlers:
            if handler(dataset, data_element):
                return
