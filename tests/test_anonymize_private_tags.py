from dicognito.anonymizer import Anonymizer

from .data_for_tests import load_test_instance


def test_mitra_global_patient_id_is_updated():
    with load_test_instance() as dataset:

        block = dataset.private_block(0x0031, "MITRA LINKED ATTRIBUTES 1.0", create=True)
        block.add_new(0x20, "LO", "GPIYMBB54")

        anonymizer = Anonymizer()
        anonymizer.anonymize(dataset)

        block = dataset.private_block(0x0031, "MITRA LINKED ATTRIBUTES 1.0")
        actual = block[0x20].value

        assert actual != "GPIYMBB54"
