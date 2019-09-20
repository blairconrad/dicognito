import collections
import datetime
import pydicom
import pydicom.dataelem
import random


class UIAnonymizer:
    def __init__(self):
        """\
        Create a new UIAnonymizer.
        """
        self._ui_map = collections.defaultdict(self._new_ui)
        self._creation_date = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        self._counter = 10000000

    def __call__(self, dataset, data_element):
        """\
        Potentially anonymize a single DataElement, replacing its
        value with something that obscures the patient's identity.

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
            data_element.value = list([self._ui_map[v] for v in data_element.value])
        else:
            data_element.value = self._ui_map[data_element.value]
        return True

    def _new_ui(self):
        self._counter += 1
        counter_part = str(self._counter)
        prefix = "2." + self._creation_date + "." + counter_part + "."
        random_begin = pow(10, 63 - len(prefix))
        random_end = pow(10, 64 - len(prefix)) - 1
        return prefix + str(random.randint(random_begin, random_end))
