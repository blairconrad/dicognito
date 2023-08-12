from dicognito.anonymizer import Anonymizer

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
