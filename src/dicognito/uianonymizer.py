import collections
import datetime
import pydicom
import pydicom.dataelem
import random


class UIAnonymizer:
    def __init__(self):
        self._ui_map = collections.defaultdict(self._new_ui)

    def __call__(self, dataset, data_element):
        if (
            data_element.VR != "UI"
            or not data_element.value
            or pydicom.datadict.keyword_for_tag(data_element.tag).endswith("ClassUID")
            or data_element.tag == pydicom.datadict.tag_for_keyword("TransferSyntaxUID")
        ):
            return False

        if pydicom.dataelem.isMultiValue(data_element.value):
            data_element.value = list([self._ui_map[v] for v in data_element.value])
        else:
            data_element.value = self._ui_map[data_element.value]
        return True

    def _new_ui(self):
        date_part = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return "2." + date_part + "." + str(random.randint(1e45, 1e46 - 1))
