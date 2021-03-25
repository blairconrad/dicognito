import pydicom


class PNAnonymizer:
    def __init__(self, randomizer, PN_lastname):
        """\
        Create a new PNAnonymizer.

        Parameters
        ----------
        randomizer : dicognito.randomizer.Randomizer
            Provides a source of randomness.
        PN_lastname : str
            assign to patient Name fields as name
        All other VR = PN fields:
            replace name with zero-length
        """
        self.randomizer = randomizer
        self.PN_lastname = PN_lastname

    def __call__(self, dataset, data_element):
        """\
        Potentially anonymize a single DataElement, replacing its
        value with something that obscures the patient's identity.

        Parameters
        ----------
        dataset : pydicom.dataset.Dataset
            The dataset to operate on.

        data_element : pydicom.dataset.DataElement
            The current element. Will be anonymized if its VR is PN.

        Returns
        -------
        True if the element was anonymized, or False if not.
        """
        if data_element.VR != "PN":
            return False
        if not data_element.value:
            return True

        if data_element.tag.group == 0x0010 and data_element.tag.element == 0x0010:
            if isinstance(data_element.value, pydicom.multival.MultiValue):
                data_element.value = [self._new_pn(original_name) for original_name in data_element.value]
            else:
                data_element.value = self._new_pn(data_element.value)
            return True
        else:
            data_element.value = ""

    def _new_pn(self, original_value):
        """
        if sex == "F":
            first_names = self._female_first_names
        elif sex == "M":
            first_names = self._male_first_names
        else:
            first_names = self._all_first_names

        if original_value:
            original_value = str(original_value).rstrip("^")
        indices = self.randomizer.get_ints_from_ranges(
            original_value, len(self._last_names), len(first_names), len(self._all_first_names)
        )
        """
        
        return self.PN_lastname
        #return self._last_names[indices[0]] + "^" + first_names[indices[1]] + "^" + self._all_first_names[indices[2]]