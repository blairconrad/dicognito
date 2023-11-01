from dicognito.anonymizer import Anonymizer
from pydicom import Dataset

from .data_for_tests import load_dcm


def test_mitra_global_patient_id_is_updated():
    with load_dcm(
        "orig_data",
        "test_mitra_global_patient_id_is_updated",
        "global_patient_id_implicit_vr.dcm",
    ) as dataset:
        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        block = dataset.private_block(0x0031, "MITRA LINKED ATTRIBUTES 1.0")
        actual = block[0x20].value

        assert actual != "GPIYMBB54"


def test_0031_0040_is_not_updated():
    with Dataset() as dataset:
        dataset.ensure_file_meta()
        dataset.add_new(0x00310040, "LO", "Some value")
        expected = dataset[0x0031, 0x0040]

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        actual = dataset[0x0031, 0x0040]
        assert actual == expected


def test_private_creator_0031_0020_is_not_updated():
    with Dataset() as dataset:
        dataset.ensure_file_meta()
        dataset.add_new(0x00310020, "LO", "Another value")
        expected = dataset[0x0031, 0x0020]

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        actual = dataset[0x0031, 0x0020]
        assert actual == expected
