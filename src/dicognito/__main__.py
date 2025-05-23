"""Anonymize one or more DICOM files' headers (not pixel data)."""

from __future__ import annotations

import glob
import logging
import os.path
import sys
from typing import TYPE_CHECKING

import pydicom

from dicognito._config import parse_arguments
from dicognito.anonymizer import Anonymizer
from dicognito.exceptions import TagError
from dicognito.filters import BurnedInAnnotationGuard, SaveInPlace, SaveToSOPInstanceUID, Summarize
from dicognito.pipeline import Pipeline
from dicognito.value_keeper import ValueKeeper

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence


def _get_filenames_from_source(source: str) -> Iterable[str]:
    if os.path.isfile(source):
        yield source
    elif os.path.isdir(source):
        for dirpath, _, filenames in os.walk(source):
            for filename in filenames:
                yield os.path.join(dirpath, filename)
    else:
        for expanded_source in glob.glob(source):
            for filename in _get_filenames_from_source(expanded_source):
                yield filename


def _get_filenames_from_sources(sources: Iterable[str]) -> Iterable[str]:
    for source in sources:
        yield from _get_filenames_from_source(source)


def _get_datasets_from_sources(sources: Iterable[str]) -> Iterable[pydicom.dataset.Dataset]:
    for filename in list(_get_filenames_from_sources(sources)):
        try:
            with pydicom.dcmread(filename, force=False) as dataset:
                yield dataset
        except pydicom.errors.InvalidDicomError:  # noqa: PERF203
            logging.info("File %s appears not to be DICOM. Skipping.", filename)


def main(main_args: Sequence[str] | None = None) -> None:
    """Run the anonymizer."""
    if main_args is None:
        main_args = sys.argv[1:]

    args = parse_arguments(main_args)

    numeric_level = getattr(logging, args.log_level.upper(), None)
    if not isinstance(numeric_level, int):
        msg = f"Invalid log level: {args.log_level}"
        raise ValueError(msg)  # noqa: TRY004
    logging.basicConfig(format="", level=numeric_level)

    if not args.in_place and not args.output_directory:
        logging.warning(
            "Neither --output-directory/-o nor --in-place/-i were specified. This will be an error in the future.",
        )

    anonymizer = Anonymizer(id_prefix=args.id_prefix, id_suffix=args.id_suffix, seed=args.seed)
    if args.keep_elements:
        try:
            for keep_element in args.keep_elements:
                anonymizer.add_element_handler(ValueKeeper(keep_element))
        except TagError as e:
            print(f"Error when attempting to keep element value: {e}", file=sys.stderr)
            sys.exit(1)

    pipeline = Pipeline()
    pipeline.add(BurnedInAnnotationGuard(args.assume_burned_in_annotation, args.on_burned_in_annotation))
    if not args.quiet:
        pipeline.add(Summarize())
    pipeline.add(args.output_directory and SaveToSOPInstanceUID(args.output_directory) or SaveInPlace())

    pipeline.before_any()

    for dataset in _get_datasets_from_sources(args.sources):
        try:
            pipeline.before_each(dataset)
            anonymizer.anonymize(dataset)
            pipeline.after_each(dataset)
        except Exception:  # noqa: PERF203
            logging.exception("Error occurred while converting %s. Aborting.", dataset.filename)
            sys.exit(1)

    pipeline.after_all()


if __name__ == "__main__":
    main()
