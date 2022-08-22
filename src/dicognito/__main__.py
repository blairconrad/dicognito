"""\
Anonymize one or more DICOM files' headers (not pixel data).
"""
from __future__ import print_function

import glob
import logging
import os.path
import sys
from typing import Iterable, Optional, Sequence

import pydicom

from dicognito._config import parse_arguments
from dicognito.anonymizer import Anonymizer
from dicognito.filters import BurnedInAnnotationGuard, SaveInPlace, SaveToSOPInstanceUID, Summarize
from dicognito.pipeline import Pipeline


def _get_filenames_from_source(source: str) -> Iterable[str]:
    if os.path.isfile(source):
        yield source
    elif os.path.isdir(source):
        for (dirpath, dirnames, filenames) in os.walk(source):
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
    for filename in _get_filenames_from_sources(sources):
        try:
            with pydicom.dcmread(filename, force=False) as dataset:
                yield dataset
        except pydicom.errors.InvalidDicomError:
            logging.info("File %s appears not to be DICOM. Skipping.", filename)


def main(main_args: Optional[Sequence[str]] = None) -> None:
    if main_args is None:
        main_args = sys.argv[1:]

    args = parse_arguments(main_args)

    numeric_level = getattr(logging, args.log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: %s" % args.log_level)
    logging.basicConfig(format="", level=numeric_level)

    anonymizer = Anonymizer(id_prefix=args.id_prefix, id_suffix=args.id_suffix, seed=args.seed)

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
        except Exception:
            logging.error("Error occurred while converting %s. Aborting.\nError was:", dataset.filename, exc_info=True)
            sys.exit(1)

    pipeline.after_all()


if __name__ == "__main__":
    main()
