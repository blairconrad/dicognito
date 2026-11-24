import difflib
import hashlib
import json
import os
from collections.abc import Iterator

import pydicom
import pytest
from pydicom.dataset import Dataset

UPDATE_VARIABLE = "DICOGNITO_UPDATE_EXPECTED_OUTPUT"


def assert_matches_expected_file(actual: str, expected_file_name: str, description: str) -> None:
    """Compare actual with the named file in tests/, or rewrite the file and fail on purpose when updating."""
    expected_path = os.path.join(os.path.dirname(__file__), expected_file_name)

    if os.environ.get(UPDATE_VARIABLE):
        with open(expected_path, mode="w", encoding="utf-8", newline="\n") as expected_file:
            expected_file.write(actual)
        pytest.fail(f"Updated {expected_path}. Review the diff, then rerun without {UPDATE_VARIABLE}.")

    with open(expected_path, encoding="utf-8") as expected_file:
        expected = expected_file.read()

    assert actual == expected, describe_differences(expected, actual, expected_file_name, description)


def format_entries(entries: list[dict[str, object]]) -> str:
    """Return a JSON array with one line per entry."""
    return "[\n" + ",\n".join(json.dumps(entry) for entry in entries) + "\n]\n"


def describe_actions(original: Dataset, anonymized: Dataset) -> list[dict[str, object]]:
    """Return one entry per element of either dataset, saying what anonymization did to it."""
    before = index_elements(original)
    after = index_elements(anonymized)
    return [with_action(before.get(path), after.get(path)) for path in sorted(before | after, key=path_order)]


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


def describe_differences(expected: str, actual: str, expected_file_name: str, description: str) -> str:
    diff = difflib.unified_diff(expected.splitlines(), actual.splitlines(), "expected", "actual", lineterm="", n=0)
    return (
        f"{description} differs from tests/{expected_file_name}. "
        "If the change is intentional, update the file (see how_to_build.md) and commit the diff.\n" + "\n".join(diff)
    )
