from itertools import dropwhile, islice, takewhile
from os.path import abspath, join
from typing import Iterator

from dicognito.anonymizer import Anonymizer


def test_anonymized_attributes_described():
    def before_description(line: str) -> bool:
        return not line.startswith("## Exactly what does dicognito do?")

    def still_description(line: str) -> bool:
        return not line.startswith("#") and not line.startswith("----")

    def drop_header(iterable: Iterator[str]) -> Iterator[str]:
        return islice(iterable, 1, None)

    data_root = abspath(join(__file__, "..", ".."))
    with open(join(data_root, "README.md"), "r") as readme:
        anonymizer = Anonymizer()

        readme_description = "".join(
            takewhile(still_description, drop_header(dropwhile(before_description, readme)))
        ).strip()
        anonymizer_description = anonymizer.describe_actions()

    print(anonymizer_description)
    assert readme_description == anonymizer_description
