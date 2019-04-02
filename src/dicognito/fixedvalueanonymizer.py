import pydicom


class FixedValueAnonymizer:
    def __init__(self, keyword, value):
        """\
        Create a new FixedValueAnonymizer.

        Parameters
        ----------
        keyword : str
            The keyword of the DICOM element to anonymize. Only
            elements with exactly this keyword will be changed.
        value
            The new value to assign to the element.
        """
        self.tag = pydicom.datadict.tag_for_keyword(keyword)
        self.value = value

    def __call__(self, dataset, data_element):
        """\
        Potentially anonymize a single DataElement, replacing its
        value with self.value.

        Parameters
        ----------
        dataset : pydicom.dataset.Dataset
            The dataset to operate on.

        data_element : pydicom.dataset.DataElement
            The current element. Will be anonymized if its keyword
            is the same as that for the keyword supplied when
            creating this anonymizer.

        Returns
        -------
        True if the element was anonymized, or False if not.
        """
        if data_element.tag == self.tag:
            data_element.value = self.value
            return True
        return False
