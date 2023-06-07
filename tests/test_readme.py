from os.path import abspath, join
from itertools import dropwhile, islice, takewhile
import pytest
from typing import Iterator

import dicognito.__main__


def test_anonymized_attributes_described(capsys):
    def before_description(line: str) -> bool:
        return not line.startswith("## Exactly what does dicognito do?")

    def still_description(line: str) -> bool:
        return not line.startswith("#") and not line.startswith("----")

    def drop_header(iterable: Iterator[str]) -> Iterator[str]:
        return islice(iterable, 1, None)

    with pytest.raises(SystemExit):
        dicognito.__main__.main(("--show-actions",))
    anonymizer_description, _ = capsys.readouterr()
    anonymizer_description = anonymizer_description.strip()

    data_root = abspath(join(__file__, "..", ".."))
    with open(join(data_root, "README.md"), "r") as readme:
        readme_description = "".join(
            takewhile(still_description, drop_header(dropwhile(before_description, readme)))
        ).strip()

    print(anonymizer_description)
    assert readme_description == anonymizer_description
