from __future__ import annotations

import itertools
import logging
import operator
import os
from typing import TYPE_CHECKING, Sequence

from dicognito.pipeline import Filter

if TYPE_CHECKING:
    import pydicom


class Summarize(Filter):
    def __init__(self) -> None:
        self.rows: list[Sequence[str]] = []

    def after_each(self, dataset: pydicom.dataset.Dataset) -> None:
        self.rows.append(
            (dataset.get("AccessionNumber", ""), dataset.get("PatientID", ""), str(dataset.get("PatientName", ""))),
        )

    def after_all(self) -> None:
        attributes = ("Accession Number", "Patient ID", "Patient Name")
        widths = [len(a) for a in attributes]

        sorted_rows = sorted(self.rows)  # type: ignore[type-var]
        output_rows = list(map(operator.itemgetter(0), itertools.groupby(sorted_rows)))
        for row in output_rows:
            for i, v in enumerate(row):
                widths[i] = max(widths[i], len(v))

        header_format = (
            "| " + " | ".join("{" + str(i) + ":^" + str(width) + "}" for (i, width) in enumerate(widths)) + " |"
        )
        row_format = header_format.replace("^", "<")
        lines = tuple("-" * width for (i, width) in enumerate(widths))

        print(header_format.format(*attributes))
        print(header_format.format(*lines))
        for row in output_rows:
            print(row_format.format(*row))


class BurnedInAnnotationGuard(Filter):
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

    def before_each(self, dataset: pydicom.dataset.Dataset) -> None:
        """\
        Guards against an undesired burned-in annotation situation, performing
        the preferred action if there's a violation.

        Parameters
        ----------
        dataset : pydicom.dataset.Dataset
            The dataset to examine.
        """

        if self._should_assume_annotation(dataset):
            self._perform_annotation_action(dataset, dataset.filename)

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


class SaveInPlace(Filter):
    def before_each(self, dataset: pydicom.dataset.Dataset) -> None:
        self.output_filename = dataset.filename

    def after_each(self, dataset: pydicom.dataset.Dataset) -> None:
        dataset.save_as(self.output_filename, write_like_original=False)


class SaveToSOPInstanceUID(Filter):
    def __init__(self, output_directory: str):
        self.output_directory = output_directory

    def before_any(self) -> None:
        if not os.path.isdir(self.output_directory):
            os.makedirs(self.output_directory)

    def after_each(self, dataset: pydicom.dataset.Dataset) -> None:
        output_filename = os.path.join(self.output_directory, dataset.SOPInstanceUID + ".dcm")
        dataset.save_as(output_filename, write_like_original=False)
