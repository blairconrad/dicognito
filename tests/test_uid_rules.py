import pytest
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.sequence import Sequence

from dicognito.anonymizer import Anonymizer


def make_dataset(**elements: object) -> Dataset:
    dataset = Dataset()
    dataset.file_meta = FileMetaDataset()
    for keyword, value in elements.items():
        setattr(dataset, keyword, value)
    return dataset


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="a registry coding scheme UID is replaced because its keyword does not end in ClassUID",
)
def test_registry_coding_scheme_uid_is_kept():
    item = Dataset()
    item.CodingSchemeUID = "1.2.840.10008.2.16.4"
    dataset = make_dataset(ConceptNameCodeSequence=Sequence([item]))

    Anonymizer(seed="uid rules").anonymize(dataset)

    assert dataset.ConceptNameCodeSequence[0].CodingSchemeUID == "1.2.840.10008.2.16.4"


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="a registry transfer syntax UID is replaced because its keyword is not TransferSyntaxUID",
)
def test_registry_referenced_transfer_syntax_uid_in_file_is_kept():
    dataset = make_dataset(ReferencedTransferSyntaxUIDInFile="1.2.840.10008.1.2.1")

    Anonymizer(seed="uid rules").anonymize(dataset)

    assert dataset.ReferencedTransferSyntaxUIDInFile == "1.2.840.10008.1.2.1"


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="a registry SOP class UID is replaced because its keyword does not end in ClassUID",
)
def test_registry_referenced_sop_class_uid_in_file_is_kept():
    dataset = make_dataset(ReferencedSOPClassUIDInFile="1.2.840.10008.5.1.4.1.1.2")

    Anonymizer(seed="uid rules").anonymize(dataset)

    assert dataset.ReferencedSOPClassUIDInFile == "1.2.840.10008.5.1.4.1.1.2"


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="a manufacturer device class UID that is not from the registry is kept because its keyword ends in ClassUID",
)
def test_non_registry_manufacturer_device_class_uid_is_replaced():
    item = Dataset()
    item.ManufacturerDeviceClassUID = "1.2.3.4.5"
    dataset = make_dataset(UDISequence=Sequence([item]))

    Anonymizer(seed="uid rules").anonymize(dataset)

    assert dataset.UDISequence[0].ManufacturerDeviceClassUID != "1.2.3.4.5"


def make_image() -> Dataset:
    return make_dataset(
        SOPClassUID="1.2.840.10008.5.1.4.1.1.2",
        SOPInstanceUID="1.2.3.4.5.6.7",
    )


def make_presentation_state() -> Dataset:
    image_item = Dataset()
    image_item.ReferencedSOPClassUID = "1.2.840.10008.5.1.4.1.1.2"
    image_item.ReferencedSOPInstanceUID = "1.2.3.4.5.6.7"
    series_item = Dataset()
    series_item.SeriesInstanceUID = "1.2.3.4.5.6"
    series_item.ReferencedImageSequence = Sequence([image_item])
    return make_dataset(
        SOPClassUID="1.2.840.10008.5.1.4.1.1.11.1",
        SOPInstanceUID="1.2.3.4.5.6.8",
        ReferencedSeriesSequence=Sequence([series_item]),
    )


@pytest.mark.parametrize("order", ["image_first", "referencing_object_first"])
def test_reference_to_image_matches_new_image_sop_instance_uid(order: str) -> None:
    anonymizer = Anonymizer(seed="uid rules")
    image = make_image()
    presentation_state = make_presentation_state()

    for dataset in [image, presentation_state] if order == "image_first" else [presentation_state, image]:
        anonymizer.anonymize(dataset)

    referenced_image = presentation_state.ReferencedSeriesSequence[0].ReferencedImageSequence[0]
    assert image.SOPInstanceUID != "1.2.3.4.5.6.7"
    assert referenced_image.ReferencedSOPInstanceUID == image.SOPInstanceUID
