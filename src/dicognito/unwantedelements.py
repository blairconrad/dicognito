"""Remove unwanted values from the data_element."""
from typing import Iterator

import pydicom

from dicognito.element_anonymizer import ElementAnonymizer


class UnwantedElementsStripper(ElementAnonymizer):
    """Unwanted element remover."""

    def __init__(self, *keywords: str):
        """
        Create a new UnwantedElementsStripper.

        Parameters
        ----------
        keywords : list of str
            All of the keywords for elements to be removed from the
            dataset.
        """
        self.tags = [pydicom.datadict.keyword_dict[keyword] for keyword in keywords]

    def __call__(self, dataset: pydicom.dataset.Dataset, data_element: pydicom.DataElement) -> bool:
        """
        Remove unwanted values from the data_element.

        Parameters
        ----------
        dataset : pydicom.dataset.Dataset
            The dataset to operate on.

        data_element : pydicom.dataset.DataElement
            The current element. Will be anonymized if its tag has a
            keyword matching one of the keywords supplied when
            creating this anonymizer.

        Returns
        -------
        True if the element was anonymized, or False if not.
        """
        if data_element.tag in self.tags:
            del dataset[data_element.tag]
            return True
        return False

    def describe_actions(self) -> Iterator[str]:
        """Describe the actions this anonymizer performs."""
        yield from (f"Remove {keyword}" for keyword in map(pydicom.datadict.keyword_for_tag, self.tags))
