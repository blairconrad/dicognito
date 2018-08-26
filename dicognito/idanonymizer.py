import pydicom
import random


class IDAnonymizer:
    _alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    def __init__(self, *tag_names):
        self.tags = [
            pydicom.datadict.tag_for_keyword(tag_name) for tag_name in tag_names
        ]

    def __call__(self, dataset, data_element):
        if data_element.tag in self.tags:
            if isinstance(data_element.value, pydicom.multival.MultiValue):
                data_element.value = [
                    self._new_text(12) for id in data_element.value
                ]
            else:
                data_element.value = self._new_text(12)
            return True
        return False

    def _new_text(self, length):
        return ''.join(random.choice(self._alphabet) for i in range(length))
