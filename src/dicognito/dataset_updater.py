import pydicom


class DatasetUpdater:
    def __call__(self, dataset: pydicom.dataset.Dataset) -> None:
        raise NotImplementedError()


class DeidentificationMethodUpdater(DatasetUpdater):
    def __call__(self, dataset: pydicom.dataset.Dataset) -> None:
        """\
        Update the DeidentificationMethod in a dataset replacing its
        value with DICOGNITO.

        Parameters
        ----------
        dataset : pydicom.dataset.Dataset
            The dataset to operate on.
        """
        if "DeidentificationMethod" not in dataset:
            dataset.DeidentificationMethod = "DICOGNITO"
            return

        existing_element = dataset.data_element("DeidentificationMethod")
        assert existing_element is not None  # satisfy mypy
        existing_value = existing_element.value

        if isinstance(existing_value, pydicom.multival.MultiValue):
            if "DICOGNITO" not in existing_value:
                existing_value.append("DICOGNITO")
        elif existing_value != "DICOGNITO":
            existing_element.value = [existing_value, "DICOGNITO"]


class PatientIdentityRemovedUpdater(DatasetUpdater):
    def __call__(self, dataset: pydicom.dataset.Dataset) -> None:
        """\
        Update the PatientIdentityRemoved in a dataset, replacing its
        value with YES as long as BurnedInAnnotation is "NO".

        Parameters
        ----------
        dataset : pydicom.dataset.Dataset
            The dataset to operate on.
        """
        if dataset.get("BurnedInAnnotation", "YES") == "NO":
            dataset.PatientIdentityRemoved = "YES"
