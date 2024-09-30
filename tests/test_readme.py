from collections.abc import Iterator
from itertools import dropwhile, islice, takewhile
from os.path import abspath, join

import pytest

import dicognito.__main__


def test_anonymized_elements_described(capsys):
    def before_description(line: str) -> bool:
        return not line.startswith("Using the default settings, dicognito will")

    def still_description(line: str) -> bool:
        return not line.startswith("#") and not line.startswith("----")

    def drop_header(iterable: Iterator[str]) -> Iterator[str]:
        return islice(iterable, 1, None)

    with pytest.raises(SystemExit):
        dicognito.__main__.main(("--what-if",))
    anonymizer_description, _ = capsys.readouterr()
    anonymizer_description = anonymizer_description.strip()

    data_root = abspath(join(__file__, "..", ".."))
    with open(join(data_root, "README.md")) as readme:
        readme_description = "".join(
            takewhile(still_description, drop_header(dropwhile(before_description, readme))),
        ).strip()

    print(anonymizer_description)
    assert readme_description == anonymizer_description
