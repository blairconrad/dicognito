import difflib
import hashlib
import json
import os
from collections.abc import Iterator

import pydicom
import pytest
from pydicom.dataset import Dataset
from pydicom.sequence import Sequence

from dicognito.anonymizer import Anonymizer

from .data_for_tests import code, load_test_instance

EXPECTED_OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "expected_seeded_output.json")
UPDATE_VARIABLE = "DICOGNITO_UPDATE_EXPECTED_OUTPUT"


def test_seeded_anonymization_matches_expected_output():
    anonymized = build_input()
    Anonymizer(seed="golden").anonymize(anonymized)
    actual = serialize(build_input(), anonymized)

    if os.environ.get(UPDATE_VARIABLE):
        with open(EXPECTED_OUTPUT_FILE, mode="w", encoding="utf-8", newline="\n") as expected_file:
            expected_file.write(actual)
        pytest.fail(f"Updated {EXPECTED_OUTPUT_FILE}. Review the diff, then rerun without {UPDATE_VARIABLE}.")

    with open(EXPECTED_OUTPUT_FILE, encoding="utf-8") as expected_file:
        expected = expected_file.read()

    assert actual == expected, describe_differences(expected, actual)


def build_input() -> Dataset:
    dataset = load_test_instance()

    dataset.OtherPatientNames = ["FIRST^OTHER", "SECOND^OTHER", "THIRD^OTHER"]
    dataset.DateOfLastCalibration = ["20100203", "20110405"]
    dataset.SOPClassesInStudy = ["1.2.840.10008.5.1.4.1.1.4", "1.2.3.4.5.6.7", "1.2.3.4.5.6.8"]

    block = dataset.private_block(0x0023, "GOLDEN PRIVATE CREATOR", create=True)
    block.add_new(0x01, "PN", "PRIVATE^PERSON")
    block.add_new(0x02, "UI", "1.2.3.4.5.6.7.8.9")
    block.add_new(0x03, "DA", "20120607")

    nested = Dataset()
    nested.PatientName = "NESTED^PERSON"
    nested.PatientID = "NESTED-ID"
    middle = Dataset()
    middle.OtherPatientIDsSequence = Sequence([nested])
    dataset.ReferencedPatientSequence = Sequence([middle])

    dataset.ContentSequence = Sequence(
        [
            content_item("PNAME", "PersonName", "SR^PERSON"),
            content_item("UIDREF", "UID", "1.2.3.4.5.6.7.8.10"),
            content_item("DATE", "Date", "20130809"),
            content_item("TIME", "Time", "101112"),
            content_item("DATETIME", "DateTime", "20140910111213"),
            content_item("TEXT", "TextValue", "Free text with Some^Name"),
        ]
    )
    return dataset


def content_item(value_type: str, keyword: str, value: str) -> Dataset:
    item = Dataset()
    item.ValueType = value_type
    item.ConceptNameCodeSequence = Sequence([code("CODE", "99GOLDEN", value_type)])
    setattr(item, keyword, value)
    return item


def serialize(original: Dataset, anonymized: Dataset) -> str:
    """Return a JSON array with one line per element of either dataset, saying what anonymization did to it."""
    before = index_elements(original)
    after = index_elements(anonymized)
    entries = [with_action(before.get(path), after.get(path)) for path in sorted(before | after, key=path_order)]
    return "[\n" + ",\n".join(json.dumps(entry) for entry in entries) + "\n]\n"


def index_elements(dataset: Dataset) -> dict[str, dict[str, object]]:
    entries = (*serialize_elements(dataset.file_meta, "file_meta/"), *serialize_elements(dataset, ""))
    return {str(entry["path"]): entry for entry in entries}


def path_order(path: str) -> tuple[bool, list[tuple[str, int]]]:
    components = []
    for component in path.removeprefix("file_meta/").split("/"):
        tag, _, index = component.partition("[")
        components.append((tag, int(index.rstrip("]")) if index else -1))
    return (not path.startswith("file_meta/"), components)


def with_action(before: dict[str, object] | None, after: dict[str, object] | None) -> dict[str, object]:
    if before is None:
        assert after is not None
        return {**after, "action": "added"}
    if after is None:
        return {"path": before["path"], "keyword": before["keyword"], "vr": before["vr"], "action": "removed"}
    if before == after:
        action = "kept"
    elif after.get("value") == [] or after.get("items") == 0:
        action = "emptied"
    else:
        action = "changed"
    return {**after, "action": action}


def serialize_elements(dataset: Dataset, path_prefix: str) -> Iterator[dict[str, object]]:
    for element in dataset:
        path = f"{path_prefix}{element.tag}"
        if element.VR == "SQ":
            yield {"path": path, "keyword": element.keyword, "vr": "SQ", "action": None, "items": len(element.value)}
            for index, item in enumerate(element.value):
                yield from serialize_elements(item, f"{path}[{index}]/")
        else:
            value = serialize_value(element)
            yield {"path": path, "keyword": element.keyword, "vr": element.VR, "action": None, "value": value}


def serialize_value(element: pydicom.DataElement) -> list[object]:
    if element.VM == 0:
        return []
    values = list(element.value) if element.VM > 1 else [element.value]
    return [serialize_scalar(value) for value in values]


def serialize_scalar(value: object) -> object:
    if isinstance(value, bytes):
        return {"length": len(value), "sha256": hashlib.sha256(value).hexdigest()}
    return str(value)


def describe_differences(expected: str, actual: str) -> str:
    diff = difflib.unified_diff(expected.splitlines(), actual.splitlines(), "expected", "actual", lineterm="", n=0)
    return (
        "Seeded anonymization output differs from tests/expected_seeded_output.json. "
        "If the change is intentional, update the file (see how_to_build.md) and commit the diff.\n" + "\n".join(diff)
    )
