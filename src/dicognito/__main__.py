"""\
Anonymize one or more DICOM files' headers (not pixel data).
"""
from __future__ import print_function
from argparse import ArgumentParser, Namespace
from typing import Any, Iterable, Optional, Sequence, Text, Tuple, Union
import sys
import argparse
import glob
import os.path
import logging
import pydicom

import dicognito
from dicognito.anonymizer import Anonymizer
from dicognito.burnedinannotationguard import BurnedInAnnotationGuard
from dicognito.summary import Summary


def main(main_args: Optional[Sequence[str]] = None) -> None:  # noqa: C901
    class VersionAction(argparse.Action):
        def __init__(
            self,
            option_strings: Sequence[str],
            version: Optional[str] = None,
            dest: str = argparse.SUPPRESS,
            default: str = argparse.SUPPRESS,
            help: str = "show program's version information and exit",
        ):
            super(VersionAction, self).__init__(
                option_strings=option_strings, dest=dest, default=default, nargs=0, help=help
            )
            self.version = version

        def __call__(
            self,
            parser: ArgumentParser,
            namespace: Namespace,
            values: Union[Text, Sequence[Any], None],
            option_string: Optional[Text] = None,
        ) -> None:
            import platform

            def print_table(version_rows: Sequence[Tuple[str, str]]) -> None:
                row_format = "{:12} | {}"
                print(row_format.format("module", "version"))
                print(row_format.format("------", "-------"))
                for module, version in version_rows:
                    # Some version strings have multiple lines and need to be squashed
                    print(row_format.format(module, version.replace("\n", " ")))

            version_rows = [
                ("platform", platform.platform()),
                ("Python", sys.version),
                ("dicognito", dicognito.__version__),
                ("pydicom", pydicom.__version__),
            ]

            print_table(version_rows)
            parser.exit()

    if main_args is None:
        main_args = sys.argv[1:]

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "sources",
        metavar="source",
        type=str,
        nargs="+",
        help="The directories or file globs (e.g. *.dcm) to anonymize. Directories "
        "will be recursed, and all files found within will be anonymized.",
    )
    parser.add_argument(
        "--id-prefix",
        "-p",
        default="",
        help="A short string prepended to each ID field, such as PatientID, "
        "AccessionNumber, and so on, to make it easier to identify anonymized "
        "studies. Longer prefixes reduce the number of available random "
        "characters in the ID and increase the chance of collisions with other "
        "IDs. May be combined with --id-suffix.",
    )
    parser.add_argument(
        "--id-suffix",
        "-s",
        default="",
        help="A short string appended to each ID field, such as PatientID, "
        "AccessionNumber, and so on, to make it easier to identify anonymized "
        "studies. Longer suffixes reduce the number of available random "
        "characters in the ID and increase the chance of collisions with other "
        "IDs. May be combined with --id-prefix.",
    )
    parser.add_argument(
        "--assume-burned-in-annotation",
        action="store",
        type=str,
        default=BurnedInAnnotationGuard.ASSUME_IF_CHOICES[0],
        choices=BurnedInAnnotationGuard.ASSUME_IF_CHOICES,
        help="How to assume the presence of burned-in annotations, considering "
        "the value of the Burned In Annotation attribute",
    )
    parser.add_argument(
        "--on-burned-in-annotation",
        action="store",
        type=str,
        default=BurnedInAnnotationGuard.IF_FOUND_CHOICES[0],
        choices=BurnedInAnnotationGuard.IF_FOUND_CHOICES,
        help="What to do when an object with assumed burned-in annotations is found",
    )
    parser.add_argument(
        "--output-directory",
        "-o",
        action="store",
        type=str,
        help="Instead of anonymizing files in-place, write anonymized files to "
        "OUTPUT_DIRECTORY, which will be created if necessary",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Reduce the verbosity of output. Suppresses summary of anonymized studies.",
    )
    parser.add_argument(
        "--log-level",
        action="store",
        metavar="LEVEL",
        default="WARNING",
        help="Set the log level. May be one of DEBUG, INFO, WARNING, ERROR, or CRITICAL.",
    )
    parser.add_argument(
        "--seed",
        help="The seed to use when generating anonymized attribute values. "
        "If the same value is supplied for subsequent dicognito invocations, then "
        "the same input objects will result in consistent anonymized results. "
        "Omitting this value allows dicognito to generate its own random seed, which "
        "may be slightly more secure, but does not support reproducible anonymization.",
    )
    parser.add_argument("--version", action=VersionAction)

    args = parser.parse_args(main_args)

    numeric_level = getattr(logging, args.log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: %s" % args.log_level)
    logging.basicConfig(format="", level=numeric_level)

    anonymizer = Anonymizer(id_prefix=args.id_prefix, id_suffix=args.id_suffix, seed=args.seed)
    burned_in_annotation_guard = BurnedInAnnotationGuard(args.assume_burned_in_annotation, args.on_burned_in_annotation)

    def get_files_from_source(source: str) -> Iterable[str]:
        if os.path.isfile(source):
            yield source
        elif os.path.isdir(source):
            for (dirpath, dirnames, filenames) in os.walk(source):
                for filename in filenames:
                    yield os.path.join(dirpath, filename)
        else:
            for expanded_source in glob.glob(source):
                for file in get_files_from_source(expanded_source):
                    yield file

    def ensure_output_directory_exists(args: Namespace) -> None:
        if args.output_directory and not os.path.isdir(args.output_directory):
            os.makedirs(args.output_directory)

    def calculate_output_filename(file: str, args: Namespace, dataset: pydicom.dataset.Dataset) -> str:
        output_file = file
        if args.output_directory:
            output_file = os.path.join(args.output_directory, dataset.SOPInstanceUID + ".dcm")
        return output_file

    ensure_output_directory_exists(args)

    summary = Summary("Accession Number", "Patient ID", "Patient Name")
    for source in args.sources:
        for file in get_files_from_source(source):
            try:
                with pydicom.dcmread(file, force=False) as dataset:
                    burned_in_annotation_guard.guard(dataset, file)
                    anonymizer.anonymize(dataset)

                    output_file = calculate_output_filename(file, args, dataset)
                    dataset.save_as(output_file, write_like_original=False)
                    summary.add_row(
                        dataset.get("AccessionNumber", ""),
                        dataset.get("PatientID", ""),
                        str(dataset.get("PatientName", "")),
                    )
            except pydicom.errors.InvalidDicomError:
                logging.info("File %s appears not to be DICOM. Skipping.", file)
                continue
            except Exception:
                logging.error("Error occurred while converting %s. Aborting.\nError was:", file, exc_info=True)
                sys.exit(1)

    if not args.quiet:
        summary.print()


if __name__ == "__main__":
    main()
