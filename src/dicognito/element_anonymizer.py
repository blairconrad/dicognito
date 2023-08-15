"""Base class for element anonymizers."""
from typing import Iterator

from pydicom import DataElement
from pydicom.dataset import Dataset


class ElementAnonymizer:
    """
    Base class for element anonymizers.

    Typically will alter (remove or change) the value of a supplied
    data_element to obscure patient identifiers. Where a DICOM attribute
    is linked to another in the same dataset (such as Study Date and Study
    Time), may alter additional elements.
    """

    def __call__(self, dataset: Dataset, data_element: DataElement) -> bool:
        """Anonymize an element (or related elements) to protect patient identity."""
        raise NotImplementedError

    def describe_actions(self) -> Iterator[str]:
        """Describe the actions this anonymizer performs."""
        raise NotImplementedError
