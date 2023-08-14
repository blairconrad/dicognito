from __future__ import annotations

from itertools import filterfalse, tee
from typing import Callable, Union, ValuesView

import pydicom
from dicognito.anonymizer import Anonymizer

from .data_for_tests import load_minimal_instance


def test_dataset_anonymizes_same_with_same_seed():
    anonymizer1 = Anonymizer(seed="SOME_FIXED_SEED")
    anonymizer2 = Anonymizer(seed="SOME_FIXED_SEED")

    with load_minimal_instance() as dataset1, load_minimal_instance() as dataset2:
        anonymizer1.anonymize(dataset1)
        anonymizer2.anonymize(dataset2)

        mismatches, matches = partition(lambda value: value == dataset2[value.tag], dataset1.values())

        assert [value.name for value in matches]
        assert not [value.name for value in mismatches]


_DatasetValue = Union[pydicom.DataElement, pydicom.dataelem.RawDataElement]


def partition(
    predicate: Callable[[_DatasetValue], bool],
    iterable: ValuesView[_DatasetValue],
    # pytest can't collect the tests when we subscript filterfalse and filter
) -> tuple[filterfalse, filter]:  # type: ignore[type-arg]
    "Use a predicate to partition entries into false entries and true entries"
    # partition(is_odd, range(10)) --> 0 2 4 6 8   and  1 3 5 7 9
    t1, t2 = tee(iterable)
    return filterfalse(predicate, t1), filter(predicate, t2)
