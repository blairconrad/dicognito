"""Actions that contribute to anonymization of a dataset."""
from __future__ import annotations

from typing import Iterator

import pydicom


class DatasetUpdater:
    """Base class for actions to work on a dataset object."""

    def __call__(self, dataset: pydicom.dataset.Dataset) -> None:
        """Alter a dataset to complement data_element-level changes."""
        raise NotImplementedError

    def describe_actions(self) -> Iterator[str]:
        """Describe the actions this anonymizer performs."""
        raise NotImplementedError


class DeidentificationMethodUpdater(DatasetUpdater):
    """Updates DeidentificationMethod."""

    def __call__(self, dataset: pydicom.dataset.Dataset) -> None:
        """
        Update DeidentificationMethod to include DICOGNITO.

        Parameters
        ----------
        dataset : pydicom.dataset.Dataset
            The dataset to operate on.
        """
        if "DeidentificationMethod" not in dataset:
            dataset.DeidentificationMethod = "DICOGNITO"
            return

        existing_element: pydicom.dataelem.DataElement | None = dataset.data_element("DeidentificationMethod")
        if not existing_element:
            dataset.DeidentificationMethod = "DICOGNITO"
            return

        existing_value = existing_element.value

        if isinstance(existing_value, pydicom.multival.MultiValue):
            if "DICOGNITO" not in existing_value:
                existing_value.append("DICOGNITO")
        elif existing_value != "DICOGNITO":
            existing_element.value = [existing_value, "DICOGNITO"]

    def describe_actions(self) -> Iterator[str]:
        """Describe the actions this anonymizer performs."""
        yield 'Add "DICOGNITO" to DeidentificationMethod'


class PatientIdentityRemovedUpdater(DatasetUpdater):
    """Updates PatientIdentityRemoved."""

    def __call__(self, dataset: pydicom.dataset.Dataset) -> None:
        """
        Replace PatientIdentityRemoved with YES as long as BurnedInAnnotation is "NO".

        Parameters
        ----------
        dataset : pydicom.dataset.Dataset
            The dataset to operate on.
        """
        if dataset.get("BurnedInAnnotation", "YES") == "NO":
            dataset.PatientIdentityRemoved = "YES"

    def describe_actions(self) -> Iterator[str]:
        """Describe the actions this anonymizer performs."""
        yield 'Set PatientIdentityRemoved to "YES" if BurnedInAnnotation is "NO"'
