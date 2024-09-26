"""Filters to apply before and after dataset anonymization."""

from __future__ import annotations

import itertools
import logging
import operator
import os
from typing import TYPE_CHECKING

from dicognito.pipeline import Filter

if TYPE_CHECKING:
    from collections.abc import Sequence

    import pydicom


class Summarize(Filter):
    """Summarizes newly-anonymized instances."""

    def __init__(self) -> None:
        """Create a new Summarize."""
        self.rows: list[Sequence[str]] = []

    def after_each(self, dataset: pydicom.dataset.Dataset) -> None:
        """Remember elements identifying anonymized instance."""
        self.rows.append(
            (dataset.get("AccessionNumber", ""), dataset.get("PatientID", ""), str(dataset.get("PatientName", ""))),
        )

    def after_all(self) -> None:
        """Output elements identifying anonymized instance."""
        elements = ("Accession Number", "Patient ID", "Patient Name")
        widths = [len(el) for el in elements]

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

        print(header_format.format(*elements))
        print(header_format.format(*lines))
        for row in output_rows:
            print(row_format.format(*row))


class BurnedInAnnotationGuard(Filter):
    """Guards against burned-in annotation foiling anonymization."""

    ASSUME_IF_CHOICES = ("if-yes", "unless-no", "never")
    IF_FOUND_CHOICES = ("warn", "fail")

    def __init__(self, assume_if: str, if_found: str):
        """
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
        """
        Guard against an undesired burned-in annotation situation.

        Perform the preferred action if there's a violation.

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
            raise ValueError(burned_in_annotation_message)
        logging.warning(burned_in_annotation_message)


class SaveInPlace(Filter):
    """Saves anonymized instances into original files."""

    def before_each(self, dataset: pydicom.dataset.Dataset) -> None:
        """Remember original filename."""
        self.output_filename = dataset.filename

    def after_each(self, dataset: pydicom.dataset.Dataset) -> None:
        """Save to original filename."""
        dataset.save_as(self.output_filename, enforce_file_format=True)


class SaveToSOPInstanceUID(Filter):
    """Saves anonymized instances to files named by new SOP Instance UID."""

    def __init__(self, output_directory: str):
        """Create a new SaveToSOPInstanceUID."""
        self.output_directory = output_directory

    def before_any(self) -> None:
        """Ensure output directory exists."""
        if not os.path.isdir(self.output_directory):
            os.makedirs(self.output_directory)

    def after_each(self, dataset: pydicom.dataset.Dataset) -> None:
        """Save anonymized instance to file named by new SOP Instance UID."""
        output_filename = os.path.join(self.output_directory, dataset.SOPInstanceUID + ".dcm")
        dataset.save_as(output_filename, enforce_file_format=True)
