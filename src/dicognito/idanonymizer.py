import pydicom


class IDAnonymizer:
    _alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    def __init__(self, randomizer, id_prefix, id_suffix, *tag_names):
        self.randomizer = randomizer
        self.id_prefix = id_prefix
        self.id_suffix = id_suffix
        self.issuer_tag = pydicom.datadict.tag_for_keyword("IssuerOfPatientID")
        self.id_tags = [
            pydicom.datadict.tag_for_keyword(tag_name) for tag_name in tag_names
        ]

        total_affixes_length = len(self.id_prefix) + len(self.id_suffix)
        self._indices_for_randomizer = [len(self._alphabet)] * (12 - total_affixes_length)

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
        id_root = "".join([self._alphabet[i] for i in
                           self.randomizer.get_ints_from_ranges(original_value, *self._indices_for_randomizer)])
        return self.id_prefix + id_root + self.id_suffix
