import datetime
import pydicom


class DateTimeAnonymizer:
    def __init__(self, offset_hours: int) -> None:
        """\
        Create a new DateTimeAnonymizer.

        Parameters
        ----------
        offset_hours : int
            The number of hours to shift dates and times by. May be
            negative or zero.
        """
        self.offset = datetime.timedelta(hours=offset_hours)

    def __call__(self, dataset: pydicom.dataset.Dataset, data_element: pydicom.DataElement) -> bool:
        """\
        Potentially anonymize one or two elements, replacing their
        value(s) with something that obscures the patient's identity.

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
        if data_element.VR != "DA" and data_element.VR != "DT":
            return False
        if not data_element.value:
            return True

        if data_element.VR == "DA":
            self._anonymize_date_and_time(dataset, data_element)
        else:
            self._anonymize_datetime(dataset, data_element)
        return True

    def _anonymize_date_and_time(self, dataset: pydicom.dataset.Dataset, data_element: pydicom.DataElement) -> None:
        date_value = data_element.value
        if isinstance(data_element.value, pydicom.multival.MultiValue):
            dates = list([v for v in data_element.value])
        else:
            dates = [data_element.value]

        times = []
        time_name = data_element.keyword.replace("Date", "Time")

        if time_name in dataset:
            time_element = dataset.data_element(time_name)
            time_value = time_element.value  # type: ignore[union-attr]
            if time_value:
                if isinstance(time_value, pydicom.multival.MultiValue):
                    times = list([v for v in time_value])
                else:
                    times = [time_value]

        new_dates = []
        new_times = []
        for i in range(len(dates)):
            date_value = dates[i]
            date_format = "%Y%m%d"
            old_date = datetime.datetime.strptime(date_value, date_format).date()

            time_value = ""
            old_hours = datetime.time()
            if i < len(times):
                time_value = times[i]
                if time_value:
                    old_hours = datetime.datetime.strptime(time_value[:2], "%H").time()
                else:
                    old_hours = datetime.time()

            old_datetime = datetime.datetime.combine(old_date, old_hours)
            new_datetime = old_datetime + self.offset

            new_dates.append(new_datetime.strftime(date_format))
            new_times.append(new_datetime.strftime("%H") + time_value[2:])

        new_dates_string = "\\".join(new_dates)
        new_times_string = "\\".join(new_times)

        data_element.value = new_dates_string
        if times:
            time_element.value = new_times_string  # type: ignore[union-attr]

    def _anonymize_datetime(self, dataset: pydicom.dataset.Dataset, data_element: pydicom.DataElement) -> None:
        if isinstance(data_element.value, pydicom.multival.MultiValue):
            datetimes = list([v for v in data_element.value])
        else:
            datetimes = [data_element.value]

        new_datetimes = []
        for datetime_value in datetimes:
            datetime_format = "%Y%m%d%H"[: len(datetime_value) - 2]

            old_datetime = datetime.datetime.strptime(datetime_value[:10], datetime_format)
            new_datetime = old_datetime + self.offset

            new_datetime_value = new_datetime.strftime(datetime_format)
            new_datetime_value += datetime_value[len(new_datetime_value) :]
            new_datetimes.append(new_datetime_value)

        data_element.value = "\\".join(new_datetimes)
