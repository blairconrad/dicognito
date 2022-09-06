import argparse
import sys
from typing import Any, Optional, Sequence, Text, Tuple, Union

import pydicom

import dicognito
from dicognito.filters import BurnedInAnnotationGuard


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
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Union[Text, Sequence[Any], None],
        option_string: Optional[Text] = None,
    ) -> None:
        import platform

        def print_table(version_rows: Sequence[Tuple[str, str]]) -> None:
            row_format = "{:12} | {}"
            print(row_format.format("module", "version"))
            print(row_format.format("-  -----", "-------"))
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


def parse_arguments(main_args: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "sources",
        metavar="source",
        type=str,
        nargs="+",
        help="The directories or file globs (e.g. *.dcm) to anonymize. Directories "
        "will be recursed, and all files found within will be anonymized.",
    )
    output_location_group = parser.add_mutually_exclusive_group()
    output_location_group.add_argument(
        "--output-directory",
        "-o",
        action="store",
        type=str,
        help="Write anonymized files to OUTPUT_DIRECTORY. The output filename will be "
        "the new SOP Instance UID. OUTPUT_DIRECTORY will be created if necessary.",
    )
    output_location_group.add_argument(
        "--in-place",
        "-i",
        action="store_true",
        help="Anonymize files in place, replacing original files. Note that repeatedly "
        "anonymizing the same files will cause date attributes to move farther into "
        "the past.",
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
    return args
