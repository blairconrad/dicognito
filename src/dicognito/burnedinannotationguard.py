import pydicom
import logging

"""\
Defines BurnedInAnnotationGuard, the class that detects and acts on assumed burned-in annotations.
"""


class BurnedInAnnotationGuard:
    ASSUME_IF_CHOICES = ["if-yes", "unless-no", "never"]
    IF_FOUND_CHOICES = ["warn", "fail"]

    def __init__(self, assume_if: str, if_found: str):
        """\
        Create a new BurnedInAnnotationGuard.

        Parameters
        ----------
        assume_if : str
            When to assume an annotation exists. Can be one of
            "if-yes", "unless-no", or "never".

        if_found : str
            What to do when an annotation is found. Can be one of
            "warn" or "fail".
        """
        self.assume_if = assume_if
        self.if_found = if_found

    def guard(self, dataset: pydicom.dataset.Dataset, filename: str) -> None:
        """\
        Guards against an undesired burned-in annotation situation, performing
        the preferred action if there's a violation.

        Parameters
        ----------
        dataset : pydicom.dataset.Dataset
            The dataset to examine.

        filename : str
            The name of the file that's the source of dataset.
        """

        if self._should_assume_annotation(dataset):
            self._perform_annotation_action(dataset, filename)

    def _should_assume_annotation(self, dataset: pydicom.dataset.Dataset) -> bool:
        burned_in_annotation = dataset.get("BurnedInAnnotation")
        return (self.assume_if == "if-yes" and burned_in_annotation == "YES") or (
            self.assume_if == "unless-no" and burned_in_annotation != "NO"
        )

    def _perform_annotation_action(self, dataset: pydicom.dataset.Dataset, filename: str) -> None:
        burned_in_annotation_value = "BurnedInAnnotation" in dataset and dataset.BurnedInAnnotation or "not specified"
        burned_in_annotation_message = "Burned In Annotation is " + burned_in_annotation_value + " in " + filename
        if self.if_found == "fail":
            raise Exception(burned_in_annotation_message)
        else:
            logging.warning(burned_in_annotation_message)
