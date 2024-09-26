"""Replace UIs with a new value."""
from collections.abc import Iterator

import pydicom
import pydicom.dataelem

from dicognito.element_anonymizer import ElementAnonymizer
from dicognito.randomizer import Randomizer


class UIAnonymizer(ElementAnonymizer):
    """
    UI anonymizer.

    Any non-empty UI will be replaced except for class UIDs and transfer syntax UIDs.
    """

    def __init__(self, randomizer: Randomizer) -> None:
        """Create a new UIAnonymizer."""
        self._randomizer = randomizer

    def __call__(
        self,
        dataset: pydicom.dataset.Dataset,  # noqa: ARG002
        data_element: pydicom.DataElement,
    ) -> bool:
        """
        Replace instance UIs with a new value.

        Parameters
        ----------
        dataset : pydicom.dataset.Dataset
            The dataset to operate on.

        data_element : pydicom.dataset.DataElement
            The current element. Will be anonymized if its VR is UI.
            If multi-valued, each item will be anonymized
            independently.

        Returns
        -------
        True if the element was anonymized, or False if not.

        """
        if (
            data_element.VR != "UI"
            or not data_element.value
            or pydicom.datadict.keyword_for_tag(data_element.tag).endswith("ClassUID")
            or data_element.tag == pydicom.datadict.tag_for_keyword("TransferSyntaxUID")
        ):
            return False

        if isinstance(data_element.value, pydicom.multival.MultiValue):
            data_element.value = [self._new_ui(v) for v in data_element.value]
        else:
            data_element.value = self._new_ui(data_element.value)
        return True

    def describe_actions(self) -> Iterator[str]:
        """Describe the actions this anonymizer performs."""
        yield "Replace all UI elements with anonymized values"

    def _new_ui(self, ui: str) -> str:
        return "2." + str(10**39 + self._randomizer.to_int(ui))
