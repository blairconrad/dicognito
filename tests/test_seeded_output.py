from pydicom.dataset import Dataset
from pydicom.sequence import Sequence

from dicognito.anonymizer import Anonymizer

from .data_for_tests import code, load_test_instance
from .expected_output import assert_matches_expected_file, describe_actions, format_entries

EXPECTED_OUTPUT_FILE_NAME = "expected_seeded_output.json"


def test_seeded_anonymization_matches_expected_output():
    anonymized = build_input()
    Anonymizer(seed="golden").anonymize(anonymized)
    actual = format_entries(describe_actions(build_input(), anonymized))

    assert_matches_expected_file(actual, EXPECTED_OUTPUT_FILE_NAME, "Seeded anonymization output")


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
