"""Replace certain values to obscure patient's identity."""
from collections.abc import Iterator

import pydicom

from dicognito.element_anonymizer import ElementAnonymizer


class FixedValueAnonymizer(ElementAnonymizer):
    """Fixed-value anonymizer."""

    def __init__(self, keyword: str, value: str) -> None:
        """
        Create a new FixedValueAnonymizer.

        Parameters
        ----------
        keyword : str
            The keyword of the DICOM element to anonymize. Only
            elements with exactly this keyword will be changed.
        value
            The new value to assign to the element.

        """
        self.tag: int = pydicom.datadict.keyword_dict[keyword]
        self.value = value

    def __call__(
        self,
        dataset: pydicom.dataset.Dataset,  # noqa: ARG002
        data_element: pydicom.DataElement,
    ) -> bool:
        """
        Replace a given value.

        Parameters
        ----------
        dataset : pydicom.dataset.Dataset
            The dataset to operate on.

        data_element : pydicom.dataset.DataElement
            The current element. Will be anonymized if its keyword
            is the same as that for the keyword supplied when
            creating this anonymizer.

        Returns
        -------
        True if the element was anonymized, or False if not.

        """
        if data_element.tag == self.tag:
            data_element.value = self.value
            return True
        return False

    def describe_actions(self) -> Iterator[str]:
        """Describe the actions this anonymizer performs."""
        yield f'Replace {pydicom.datadict.keyword_for_tag(self.tag)} with "{self.value}"'
