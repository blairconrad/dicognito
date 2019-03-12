import pydicom


class IDAnonymizer:
    _alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    _id_length = 12
    _indices_for_randomizer = [len(_alphabet)] * _id_length

    def __init__(self, randomizer, *tag_names):
        self.randomizer = randomizer
        self.issuer_tag = pydicom.datadict.tag_for_keyword("IssuerOfPatientID")
        self.id_tags = [
            pydicom.datadict.tag_for_keyword(tag_name) for tag_name in tag_names
        ]

    def __call__(self, dataset, data_element):
        if data_element.tag in self.id_tags:
            if isinstance(data_element.value, pydicom.multival.MultiValue):
                data_element.value = [
                    self._new_id(id) for id in data_element.value
                ]
            else:
                data_element.value = self._new_id(data_element.value)
            return True
        if data_element.tag == self.issuer_tag and data_element.value:
            data_element.value = "DICOGNITO"
        return False

    def _new_id(self, original_value):
        return ''.join([self._alphabet[i]
                        for i in self.randomizer.get_ints_from_ranges(original_value, *self._indices_for_randomizer)])
