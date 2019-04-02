import pydicom


class IDAnonymizer:
    _alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    def __init__(self, randomizer, id_prefix, id_suffix, *keywords):
        """\
        Create a new IDAnonymizer.

        Parameters
        ----------
        randomizer : dicognito.randomizer.Randomizer
            Provides a source of randomness.
        id_prefix : str
            A prefix to add to all unstructured ID fields, such as Patient
            ID, Accession Number, etc.
        id_suffix : str
            A prefix to add to all unstructured ID fields, such as Patient
            ID, Accession Number, etc.
        keywords : list of str
            All of the keywords for elements to be anonymized. Only
            elements with matching keywords will be updated.
        """
        self.randomizer = randomizer
        self.id_prefix = id_prefix
        self.id_suffix = id_suffix
        self.issuer_tag = pydicom.datadict.tag_for_keyword("IssuerOfPatientID")
        self.id_tags = [pydicom.datadict.tag_for_keyword(tag_name) for tag_name in keywords]

        total_affixes_length = len(self.id_prefix) + len(self.id_suffix)
        self._indices_for_randomizer = [len(self._alphabet)] * (12 - total_affixes_length)

    def __call__(self, dataset, data_element):
        """\
        Potentially anonymize a single DataElement, replacing its
        value with something that obscures the patient's identity.

        Parameters
        ----------
        dataset : pydicom.dataset.Dataset
            The dataset to operate on.

        data_element : pydicom.dataset.DataElement
            The current element. Will be anonymized if it has a value
            and if its keyword matches one of the keywords supplied when
            creating this anonymizer or matches IssuerOfPatientID.

            The element may be multi-valued, in which case each item is
            anonymized independently.

        Returns
        -------
        True if the element was anonymized, or False if not.
        """
        if data_element.tag in self.id_tags:
            if isinstance(data_element.value, pydicom.multival.MultiValue):
                data_element.value = [self._new_id(id) for id in data_element.value]
            else:
                data_element.value = self._new_id(data_element.value)
            return True
        if data_element.tag == self.issuer_tag and data_element.value:
            data_element.value = "DICOGNITO"
            return True
        return False

    def _new_id(self, original_value):
        indexes = self.randomizer.get_ints_from_ranges(original_value, *self._indices_for_randomizer)
        id_root = "".join([self._alphabet[i] for i in indexes])
        return self.id_prefix + id_root + self.id_suffix
