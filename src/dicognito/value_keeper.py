"""Retains an element's value."""

import re
from collections.abc import Iterator

import pydicom

from dicognito.element_anonymizer import ElementAnonymizer
from dicognito.exceptions import TagError


class ValueKeeper(ElementAnonymizer):
    """Value keeper - keeps existing values."""

    def __init__(self, tag_name: str) -> None:
        """
        Create a new ValueKeeper.

        Parameters
        ----------
        tag_name : str
            A string that identifies the DICOM element to preserve.
            Must be the well-known name of a DICOM element or must represent
            a numeric DICOM tag and be in the form "stuv,wxyz" where each
            of the characters is a hexadecimal digit.

        """
        self._tag: int = self._tag_from_name(tag_name)

    def __call__(
        self,
        dataset: pydicom.dataset.Dataset,  # noqa: ARG002
        data_element: pydicom.DataElement,
    ) -> bool:
        """
        Keep a given element's value as-is.

        Parameters
        ----------
        dataset : pydicom.dataset.Dataset
            The dataset to operate on.

        data_element : pydicom.dataset.DataElement
            The current element. Will be kept if its tag
            is the same as that for the tag referenced when
            creating this "anonymizer".

        Returns
        -------
        True if the element was preserved, or False if not.

        """
        return data_element.tag == self._tag and True or False

    def describe_actions(self) -> Iterator[str]:
        """Describe the actions this anonymizer performs."""
        tag_name = pydicom.datadict.keyword_for_tag(self._tag)
        if not tag_name:
            group = self._tag >> 16
            elem = self._tag & 0xFFFF
            tag_name = f"{group:04X},{elem:04X}"
        yield f"Keep {tag_name} values"

    def _tag_from_name(self, tag_name: str) -> int:
        match = re.fullmatch("([0-9A-F]{4}),([0-9A-F]{4})", tag_name)
        if match:
            return int(match.group(1) + match.group(2), base=16)
        try:
            return pydicom.datadict.keyword_dict[tag_name]
        except KeyError:
            raise TagError(tag_name) from None
