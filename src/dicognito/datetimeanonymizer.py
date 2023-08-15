"""Replace date-based values with something that obscures the patient's identity."""

import datetime
from itertools import zip_longest
from typing import Iterator, MutableSequence

import pydicom

from dicognito.element_anonymizer import ElementAnonymizer


class DateTimeAnonymizer(ElementAnonymizer):
    """Date/time anonymizers."""

    def __init__(self, offset_hours: int) -> None:
        """
        Create a new DateTimeAnonymizer.

        Parameters
        ----------
        offset_hours : int
            The number of hours to shift dates and times by. May be
            negative or zero.
        """
        self.offset = datetime.timedelta(hours=offset_hours)

    def __call__(self, dataset: pydicom.dataset.Dataset, data_element: pydicom.DataElement) -> bool:
        """
        Replace DT or DA (and TM) values with something that obscures patient identity.

        Parameters
        ----------
        dataset : pydicom.dataset.Dataset
            The dataset to operate on.

        data_element : pydicom.dataset.DataElement
            The current element. Will be anonymized if it has VR DA
            or DT. If it has value DA, the corresponding TM will also
            be anonymized.

        Returns
        -------
        True if an element (or two) was anonymized, or False if not.
        """
        if data_element.VR not in ("DA", "DT"):
            return False
        if not data_element.value:
            return True

        if data_element.VR == "DA":
            self._anonymize_date_and_time(dataset, data_element)
        else:
            self._anonymize_datetime(data_element)
        return True

    def describe_actions(self) -> Iterator[str]:
        """Describe the actions this anonymizer performs."""
        yield "Replace all DA attributes with anonymized values that precede the originals"
        yield "Replace all DT attributes with anonymized values that precede the originals"
        yield "Replace all TM attributes with anonymized values that precede the originals"

    def _anonymize_date_and_time(self, dataset: pydicom.dataset.Dataset, data_element: pydicom.DataElement) -> None:
        dates = self._get_value_as_sequence(data_element)

        times: MutableSequence[str] = []
        time_name = data_element.keyword.replace("Date", "Time")

        if time_name in dataset:
            time_element = dataset.data_element(time_name)
            if time_element and time_element.value:
                times = self._get_value_as_sequence(time_element)

        new_dates = []
        new_times = []

        for date, time in zip_longest(dates, times, fillvalue=""):
            new_datetime = self._shift_datetime(date + time)

            new_dates.append(new_datetime[:8])
            new_times.append(new_datetime[8:])

        data_element.value = new_dates
        if times:
            time_element.value = new_times  # type: ignore[union-attr]

    def _anonymize_datetime(self, data_element: pydicom.DataElement) -> None:
        datetimes = self._get_value_as_sequence(data_element)
        data_element.value = [self._shift_datetime(datetime_value) for datetime_value in datetimes]

    def _shift_datetime(self, datetime_value: str) -> str:
        datetime_format = "%Y%m%d%H"[: len(datetime_value) - 2]

        old_datetime = datetime.datetime.strptime(datetime_value[:10], datetime_format)  # noqa: DTZ007
        new_datetime = old_datetime + self.offset

        new_datetime_value = new_datetime.strftime(datetime_format)
        new_datetime_value += datetime_value[len(new_datetime_value) :]

        return new_datetime_value

    def _get_value_as_sequence(self, data_element: pydicom.DataElement) -> MutableSequence[str]:
        if isinstance(data_element.value, pydicom.multival.MultiValue):
            return data_element.value
        return [data_element.value]
