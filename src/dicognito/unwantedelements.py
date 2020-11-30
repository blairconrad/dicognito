import pydicom


class UnwantedElementsStripper:
    def __init__(self, *keywords: str):
        """\
        Create a new UnwantedElementsStripper.

        Parameters
        ----------
        keywords : list of str
            All of the keywords for elements to be removed from the
            dataset.
        """
        self.tags = [pydicom.datadict.tag_for_keyword(keyword) for keyword in keywords]

    def __call__(self, dataset: pydicom.dataset.Dataset, data_element: pydicom.DataElement) -> bool:
        """\
        Potentially anonymize a single DataElement, removing its value
        if the data_element's keyword matches one of those supplied when
        this anonymizer was created.

        Parameters
        ----------
        dataset : pydicom.dataset.Dataset
            The dataset to operate on.

        data_element : pydicom.dataset.DataElement
            The current element. Will be anonymized if its tag has a
            keyword matching one of the keywords supplied when
            creating this anonymizer.

        Returns
        -------
        True if the element was anonymized, or False if not.
        """
        if data_element.tag in self.tags:
            del dataset[data_element.tag]
            return True
        return False
