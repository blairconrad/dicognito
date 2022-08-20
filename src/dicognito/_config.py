import argparse
import dicognito
import pydicom
import sys
from typing import Any, Optional, Sequence, Text, Tuple, Union


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
