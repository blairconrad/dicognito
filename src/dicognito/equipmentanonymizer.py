import pydicom


class EquipmentAnonymizer:
    def __init__(self, address_anonymizer):
        self.address_anonymizer = address_anonymizer

        self._element_anonymizers = {
            pydicom.datadict.tag_for_keyword("InstitutionName"): self.anonymize_institution_name,
            pydicom.datadict.tag_for_keyword("InstitutionAddress"): self.anonymize_institution_address,
            pydicom.datadict.tag_for_keyword("InstitutionalDepartmentName"): self.anonymize_department_name,
            pydicom.datadict.tag_for_keyword("StationName"): self.anonymize_station_name,
        }

    def __call__(self, dataset, data_element):
        element_anonymizer = self._element_anonymizers.get(
            data_element.tag, None
        )
        if not element_anonymizer:
            return False

        element_anonymizer(dataset, data_element)

    def anonymize_institution_name(self, dataset, data_element):
        region = self.address_anonymizer.get_region(data_element.value)
        dataset.InstitutionAddress = " ".join([
            self.address_anonymizer.get_street_address(data_element.value),
            region,
            self.address_anonymizer.get_country(data_element.value)
        ])
        data_element.value = region + " CLINIC"

    def anonymize_institution_address(self, dataset, data_element):
        # handled by anonymize_institution_name
        pass

    def anonymize_department_name(self, dataset, data_element):
        data_element.value = 'RADIOLOGY'

    def anonymize_station_name(self, dataset, data_element):
        data_element.value = dataset.Modality + '01'
