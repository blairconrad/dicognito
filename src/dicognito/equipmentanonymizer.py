import pydicom


class EquipmentAnonymizer:
    def __init__(self, address_anonymizer):
        """\
        Create a new EquipmentAnonymizer.

        Parameters
        ----------
        address_anonymizer : dicognito.addressanonymizer.AddressAnonymizer
            Provides anonymized address components.
        """
        self.address_anonymizer = address_anonymizer

        self._element_anonymizers = {
            pydicom.datadict.tag_for_keyword("InstitutionName"): self.anonymize_institution_name,
            pydicom.datadict.tag_for_keyword("InstitutionAddress"): self.anonymize_institution_address,
            pydicom.datadict.tag_for_keyword("InstitutionalDepartmentName"): self.anonymize_department_name,
            pydicom.datadict.tag_for_keyword("StationName"): self.anonymize_station_name,
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
            and if its keyword is one of InstitutionName,
            InstitutionAddress, InstitutionalDepartmentName, or
            StationName. Additionally, if its keyword is InstitutionName,
            then InstitutionAddress will also be anonymized.

        Returns
        -------
        True if the element was anonymized, or False if not.
        """
        element_anonymizer = self._element_anonymizers.get(data_element.tag, None)
        if not element_anonymizer:
            return False

        element_anonymizer(dataset, data_element)

    def anonymize_institution_name(self, dataset, data_element):
        region = self.address_anonymizer.get_region(data_element.value)
        street_address = self.address_anonymizer.get_street_address(data_element.value)
        street = street_address.split(" ", 1)[1]
        dataset.InstitutionAddress = ", ".join(
            [street_address, region, self.address_anonymizer.get_country(data_element.value)]
        )
        data_element.value = region + "'S " + street + " CLINIC"

    def anonymize_institution_address(self, dataset, data_element):
        # handled by anonymize_institution_name
        pass

    def anonymize_department_name(self, dataset, data_element):
        data_element.value = "RADIOLOGY"

    def anonymize_station_name(self, dataset, data_element):
        data_element.value = dataset.Modality + "01"
