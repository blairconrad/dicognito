import pydicom
import pytest
from pydicom.dataset import Dataset, FileMetaDataset

from dicognito.anonymizer import Anonymizer

UNPARSEABLE_VALUES = [
    pytest.param("UNKNOWN", id="unknown"),
    pytest.param("00000000", id="zeros"),
    pytest.param("20200230", id="impossible-day"),
    pytest.param("20200102-20200105", id="range"),
    pytest.param(["20200102", ""], id="empty-component"),
]


@pytest.mark.xfail(strict=True, raises=ValueError, reason="an unparseable date or datetime raises ValueError")
@pytest.mark.filterwarnings("ignore:Invalid value for VR")
@pytest.mark.parametrize("keyword", ["StudyDate", "AcquisitionDateTime"])
@pytest.mark.parametrize("original_value", UNPARSEABLE_VALUES)
def test_unparseable_date_does_not_raise_or_survive(keyword, original_value):
    dataset = Dataset()
    dataset.file_meta = FileMetaDataset()
    setattr(dataset, keyword, original_value)
    original_components = [original_value] if isinstance(original_value, str) else original_value

    Anonymizer(seed="unparseable dates").anonymize(dataset)

    anonymized_components = []
    if keyword in dataset:
        anonymized_value = dataset[keyword].value
        is_multi_valued = isinstance(anonymized_value, pydicom.multival.MultiValue)
        anonymized_components = [
            str(component) for component in (anonymized_value if is_multi_valued else [anonymized_value])
        ]
    survivors = [component for component in original_components if component and component in anonymized_components]
    assert survivors == []
