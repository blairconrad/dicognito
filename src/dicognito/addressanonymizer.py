import pydicom

"""\
Defines AddressAnonymizer, responsible for anonymizing addresses
"""


class AddressAnonymizer:
    """\
    Anonymizes addresses.
    """

    def __init__(self, randomizer):
        """\
        Create a new AddressAnonymizer.

        Parameters
        ----------
        randomizer : dicognito.randomizer.Randomizer
            Provides a source of randomness.
        """
        self.randomizer = randomizer

        address_tag = pydicom.datadict.tag_for_keyword("PatientAddress")
        region_tag = pydicom.datadict.tag_for_keyword("RegionOfResidence")
        country_tag = pydicom.datadict.tag_for_keyword("CountryOfResidence")

        self._value_factories = {
            address_tag: "",
            region_tag: "",
            country_tag: "",
        }

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
            and if its keyword is one of PatientAddress, RegionOfResidence,
            or CountryOfResidences.

        Returns
        -------
        True if the element was anonymized, or False if not.
        """
        value_factory = self._value_factories.get(data_element.tag, None)
        if not value_factory:
            return False
        if not data_element.value:
            return True

        data_element.value = value_factory(data_element.value)
        return True