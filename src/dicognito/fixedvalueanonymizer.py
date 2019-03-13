import pydicom


class FixedValueAnonymizer:
    def __init__(self, tag_name, value):
        self.tag = pydicom.datadict.tag_for_keyword(tag_name)
        self.value = value

    def __call__(self, dataset, data_element):
        if data_element.tag == self.tag:
            data_element.value = self.value
            return True
        return False
