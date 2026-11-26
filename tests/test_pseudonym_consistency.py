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


@pytest.mark.xfail(strict=True, raises=AssertionError, reason="I-1 a person's pseudonym depends on PatientSex")
def test_same_referring_physician_gets_one_pseudonym_regardless_of_patient_sex():
    anonymizer = Anonymizer(seed="pseudonym consistency")
    pseudonyms = set()
    for patient_sex in ["F", "M", None]:
        dataset = make_dataset(ReferringPhysicianName="WELBY^MARCUS")
        if patient_sex is not None:
            dataset.PatientSex = patient_sex

        anonymizer.anonymize(dataset)

        pseudonyms.add(str(dataset.ReferringPhysicianName))

    assert len(pseudonyms) == 1


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="I-1 a name in a sequence item does not see the top-level PatientSex",
)
def test_same_performing_physician_gets_one_pseudonym_at_top_level_and_in_sequence_item():
    dataset = make_dataset(PatientSex="F", PerformingPhysicianName="HOUSE^GREGORY")
    item = Dataset()
    item.PerformingPhysicianName = "HOUSE^GREGORY"
    dataset.PerformedSeriesSequence = Sequence([item])

    Anonymizer(seed="pseudonym consistency").anonymize(dataset)

    assert dataset.PerformingPhysicianName == dataset.PerformedSeriesSequence[0].PerformingPhysicianName


@pytest.mark.xfail(strict=True, raises=AssertionError, reason="I-2 every IssuerOfPatientID becomes DICOGNITO")
def test_same_patient_id_from_different_issuers_gives_different_patients():
    anonymizer = Anonymizer(seed="pseudonym consistency")
    patients = set()
    for issuer in ["HOSP_A", "HOSP_B"]:
        dataset = make_dataset(PatientID="123", IssuerOfPatientID=issuer)

        anonymizer.anonymize(dataset)

        patients.add((dataset.PatientID, dataset.IssuerOfPatientID))

    assert len(patients) == 2  # noqa: PLR2004


def test_same_patient_id_and_issuer_gives_same_patient():
    anonymizer = Anonymizer(seed="pseudonym consistency")
    patients = set()
    for _ in range(2):
        dataset = make_dataset(PatientID="123", IssuerOfPatientID="HOSP_A")

        anonymizer.anonymize(dataset)

        patients.add((dataset.PatientID, dataset.IssuerOfPatientID))

    assert len(patients) == 1
    new_patient_id, new_issuer = patients.pop()
    assert new_patient_id != "123"
    assert new_issuer != "HOSP_A"
