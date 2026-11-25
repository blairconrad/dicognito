import json
import os

from pydicom.datadict import dictionary_VR, keyword_for_tag
from pydicom.dataset import Dataset
from pydicom.tag import Tag

from dicognito.anonymizer import Anonymizer

from .expected_output import assert_matches_expected_file, describe_actions, format_entries

TABLE_PATH = os.path.join(os.path.dirname(__file__), "ps315_table_2024b.json")
SUBJECT = "ps315_output"

SAMPLE_VALUES: dict[str, object] = {
    "AE": "SAMPLEAE",
    "AS": "045Y",
    "AT": 0x00100010,
    "CS": "SAMPLE",
    "DA": "20200102",
    "DS": "1.5",
    "DT": "20200102123456",
    "FD": 1.0,
    "FL": 1.0,
    "IS": "3",
    "LO": "SAMPLE LO",
    "LT": "sample text",
    "OB": b"\x01\x02",
    "OD": b"\x00" * 8,
    "OF": b"\x00" * 4,
    "OL": b"\x00" * 4,
    "OV": b"\x00" * 8,
    "OW": b"\x01\x02",
    "PN": "DOE^JOHN",
    "SH": "SAMPLESH",
    "SL": 1,
    "SS": 1,
    "ST": "sample text",
    "SV": 1,
    "TM": "123456",
    "UC": "sample",
    "UI": "1.2.3.4.5",
    "UL": 1,
    "UN": b"\x01\x02",
    "UR": "http://example.org/x",
    "US": 1,
    "UT": "sample text",
    "UV": 1,
}


def test_ps315_anonymization_matches_expected_output():
    with open(TABLE_PATH, encoding="utf-8") as table_file:
        attributes = json.load(table_file)["attributes"]

    actual = format_entries([describe_attribute(attribute) for attribute in sorted(attributes, key=lambda a: a["id"])])

    assert_matches_expected_file(actual, SUBJECT, "PS3.15 Table E.1-1 anonymization output")


def describe_attribute(attribute: dict[str, str]) -> dict[str, object]:
    entry: dict[str, object] = {
        "tag": attribute["tag"],
        "name": attribute["name"],
        "profile": attribute["basicProfile"],
    }
    try:
        tag = int(attribute["id"], 16)
    except ValueError:
        return {**entry, "skipped": "wildcard tag"}
    try:
        vr = dictionary_VR(tag).split(" or ")[0]
    except KeyError:
        return {**entry, "skipped": "not in the pydicom dictionary"}

    return {
        "tag": attribute["tag"],
        "keyword": keyword_for_tag(tag),
        "vr": vr,
        "profile": attribute["basicProfile"],
        "populated": anonymize_attribute(tag, vr, populated=True),
        "empty": anonymize_attribute(tag, vr, populated=False),
    }


def anonymize_attribute(tag: int, vr: str, *, populated: bool) -> dict[str, object]:
    try:
        anonymized = build_input(tag, vr, populated=populated)
        Anonymizer(seed="ps315").anonymize(anonymized)
        actions = describe_actions(build_input(tag, vr, populated=populated), anonymized)
    except Exception as error:  # noqa: BLE001
        return {"action": f"error: {type(error).__name__}"}

    path = str(Tag(tag))
    outcome: dict[str, object] = {"action": "removed"}
    nested = []
    for action in actions:
        if action["path"] == path:
            outcome = outcome_of(action)
        elif str(action["path"]).startswith(path + "["):
            nested.append({"path": str(action["path"]).removeprefix(path), **outcome_of(action)})
    return {**outcome, "nested": nested} if nested else outcome


def outcome_of(action: dict[str, object]) -> dict[str, object]:
    return {key: action[key] for key in ("action", "value", "items") if key in action}


def build_input(tag: int, vr: str, *, populated: bool) -> Dataset:
    dataset = Dataset()
    dataset.ensure_file_meta()
    if vr == "SQ":
        item = Dataset()
        if populated:
            item.CodeValue = "X"
        dataset.add_new(tag, vr, [item] if populated else [])
    elif populated:
        dataset.add_new(tag, vr, SAMPLE_VALUES[vr])
    else:
        dataset.add_new(tag, vr, "" if isinstance(SAMPLE_VALUES[vr], str) else None)
    return dataset
