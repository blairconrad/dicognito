from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pydicom

"""\
A framework for running additional tasks using the datasets that will be
anonymized. Like Unix commands, a pipeline consists of a list of Filters.
A Filter is a single part of the pipeline that has an opportunity to act

1. before any datasets are anonymized,
2. before each dataset is anonymized,
3. after each dataset has been anonymized, and finally
4. after all the datasets have been anonymized

For each "before" stage, the filters will be executed in the order they were
added to the pipeline, and for each "after" stage, the Filters will be executed
in reverse order.

If a Pipeline is created with two Filters
>>> pipeline = Pipeline()
>>> pipeline.add(Filter1())
>>> pipeline.add(Filter2())

And run as an anonymization session on two datasets, the following calls would be made:

* Filter1.before_any()
* Filter2.before_any()

* Filter1.before_each(dataset1)
* Filter2.before_each(dataset1)
* Filter2.after_each(dataset1)
* Filter1.after_each(dataset1)

* Filter1.before_each(dataset2)
* Filter2.before_each(dataset2)
* Filter2.after_each(dataset2)
* Filter1.after_each(dataset2)

* Filter2.after_all()
* Filter1.after_all()
"""


class Filter:
    def before_any(self) -> None:
        """Run before any datasets are anonymized"""
        pass

    def before_each(self, dataset: pydicom.dataset.Dataset) -> None:
        """Run on each dataset before it is anonymized"""
        pass

    def after_each(self, dataset: pydicom.dataset.Dataset) -> None:
        """Run on each dataset after it has been anonymized"""
        pass

    def after_all(self) -> None:
        """Run after all datasets have been anonymized"""
        pass


class Pipeline:
    def __init__(self) -> None:
        self.filters: list[Filter] = []

    def add(self, new_filter: Filter) -> None:
        self.filters.append(new_filter)

    def before_any(self) -> None:
        for a_filter in self.filters:
            a_filter.before_any()

    def before_each(self, dataset: pydicom.dataset.Dataset) -> None:
        for a_filter in self.filters:
            a_filter.before_each(dataset)

    def after_each(self, dataset: pydicom.dataset.Dataset) -> None:
        for a_filter in self.filters[::-1]:
            a_filter.after_each(dataset)

    def after_all(self) -> None:
        for a_filter in self.filters[::-1]:
            a_filter.after_all()
