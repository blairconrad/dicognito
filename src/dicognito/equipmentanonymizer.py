"""Replace equipment-related values with something that obscures the patient's identity."""

from collections.abc import Iterator

import pydicom

from dicognito.addressanonymizer import AddressAnonymizer
from dicognito.element_anonymizer import ElementAnonymizer


class EquipmentAnonymizer(ElementAnonymizer):
    """Equipment anonymizer."""

    def __init__(self, address_anonymizer: AddressAnonymizer) -> None:
        """
        Create a new EquipmentAnonymizer.

        Parameters
        ----------
        address_anonymizer : dicognito.addressanonymizer.AddressAnonymizer
            Provides anonymized address components.

        """
        self.address_anonymizer = address_anonymizer

        self._element_anonymizers = {
            pydicom.datadict.keyword_dict["InstitutionName"]: self._anonymize_institution_name,
            pydicom.datadict.keyword_dict["InstitutionAddress"]: self._anonymize_institution_address,
            pydicom.datadict.keyword_dict["InstitutionalDepartmentName"]: self._anonymize_department_name,
        }

    def __call__(self, dataset: pydicom.dataset.Dataset, data_element: pydicom.DataElement) -> bool:
        """
        Replace equipment-related values with something that obscures the patient's identity.

        Parameters
        ----------
        dataset : pydicom.dataset.Dataset
            The dataset to operate on.

        data_element : pydicom.dataset.DataElement
            The current element. Will be anonymized if it has a value
            and if its keyword is one of InstitutionName,
            InstitutionAddress, or InstitutionalDepartmentName.
            Additionally, if its keyword is InstitutionName,
            then InstitutionAddress will also be anonymized.

        Returns
        -------
        True if the element was anonymized, or False if not.

        """
        element_anonymizer = self._element_anonymizers.get(data_element.tag, None)
        if not element_anonymizer:
            return False

        element_anonymizer(dataset, data_element)
        return True

    def describe_actions(self) -> Iterator[str]:
        """Describe the actions this anonymizer performs."""
        yield "Replace InstitutionName with anonymized values"
        yield "Replace InstitutionAddress with anonymized values (only if replacing matching InstitutionName element)"
        yield 'Replace InstitutionalDepartmentName with "RADIOLOGY"'

    def _anonymize_institution_name(self, dataset: pydicom.dataset.Dataset, data_element: pydicom.DataElement) -> None:
        region = self.address_anonymizer.get_region(data_element.value)
        street_address = self.address_anonymizer.get_street_address(data_element.value)
        street = street_address.split(" ", 1)[1]
        dataset.InstitutionAddress = ", ".join(
            [street_address, region, self.address_anonymizer.get_country(data_element.value)],
        )
        data_element.value = region + "'S " + street + " CLINIC"

    def _anonymize_institution_address(
        self,
        dataset: pydicom.dataset.Dataset,
        data_element: pydicom.DataElement,
    ) -> None:
        # handled by _anonymize_institution_name
        pass

    def _anonymize_department_name(
        self,
        dataset: pydicom.dataset.Dataset,  # noqa: ARG002
        data_element: pydicom.DataElement,
    ) -> None:
        data_element.value = "RADIOLOGY"
