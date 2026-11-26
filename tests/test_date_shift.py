import datetime as dt

import pytest
from pydicom.dataset import Dataset, FileMetaDataset

from dicognito.anonymizer import Anonymizer
from dicognito.value_keeper import ValueKeeper


def make_dataset(**elements: object) -> Dataset:
    dataset = Dataset()
    dataset.file_meta = FileMetaDataset()
    for keyword, value in elements.items():
        setattr(dataset, keyword, value)
    return dataset


def to_datetime(value: str) -> dt.datetime:
    return dt.datetime.strptime(value, "%Y%m%d%H%M%S")  # noqa: DTZ007


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="I-3 dates are shifted by hours, so a date with a time can move to another day",
)
def test_same_date_with_and_without_time_shifts_to_same_date():
    dataset = make_dataset(StudyDate="20200102", StudyTime="230000", SeriesDate="20200102")

    Anonymizer(seed="date shift").anonymize(dataset)

    assert dataset.StudyDate == dataset.SeriesDate


@pytest.mark.xfail(strict=True, raises=AssertionError, reason="I-3 dates are shifted by hours, not whole days")
def test_date_shift_is_whole_days():
    partial_day_shifts = {}
    for seed in range(20):
        dataset = make_dataset(StudyDate="20200102", StudyTime="101010", AcquisitionDateTime="20200102101010")

        Anonymizer(seed=str(seed)).anonymize(dataset)

        original = to_datetime("20200102101010")
        for keyword, new_value in [
            ("StudyDate", dataset.StudyDate + dataset.StudyTime),
            ("AcquisitionDateTime", dataset.AcquisitionDateTime),
        ]:
            shift = original - to_datetime(new_value)
            if shift.seconds != 0:
                partial_day_shifts[(seed, keyword)] = shift

    assert partial_day_shifts == {}


@pytest.mark.xfail(strict=True, raises=AssertionError, reason="I-4 a time without its paired date is not shifted")
def test_time_without_date_keeps_difference_from_time_with_date():
    dataset = make_dataset(StudyDate="20200102", StudyTime="100000", SeriesTime="100200")

    Anonymizer(seed="date shift").anonymize(dataset)

    difference = to_datetime("20200102" + dataset.SeriesTime) - to_datetime("20200102" + dataset.StudyTime)
    assert difference == dt.timedelta(minutes=2)


@pytest.mark.xfail(strict=True, raises=AssertionError, reason="I-5 the StudyDate handler changes StudyTime")
def test_keeping_time_keeps_time():
    dataset = make_dataset(StudyDate="20200102", StudyTime="100000")

    anonymizer = Anonymizer(seed="date shift")
    anonymizer.add_element_handler(ValueKeeper("StudyTime"))
    anonymizer.anonymize(dataset)

    assert dataset.StudyTime == "100000"
