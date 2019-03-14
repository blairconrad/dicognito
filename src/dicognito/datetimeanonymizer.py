import datetime


class DateTimeAnonymizer:
    def __init__(self, offset_hours):
        self.offset = datetime.timedelta(hours=offset_hours)

    def __call__(self, dataset, data_element):
        if data_element.VR != "DA" and data_element.VR != "DT":
            return False
        if not data_element.value:
            return True

        if data_element.VR == "DA":
            self._anonymize_date_and_time(dataset, data_element)
        else:
            self._anonymize_datetime(dataset, data_element)
        return True

    def _anonymize_date_and_time(self, dataset, data_element):
        date_value = data_element.value
        date_format = "%Y%m%d"[:len(date_value)-2]

        old_date = datetime.datetime.strptime(date_value, date_format).date()

        old_hours = datetime.time()
        time_value = ""
        time_name = data_element.keyword[:-4] + "Time"
        if time_name in dataset:
            time_value = dataset.data_element(time_name).value
            if time_value:
                old_hours = datetime.datetime.strptime(
                    time_value[:2], "%H").time()

        old_datetime = datetime.datetime.combine(old_date, old_hours)
        new_datetime = old_datetime + self.offset

        data_element.value = new_datetime.strftime(date_format)
        if time_value:
            dataset.data_element(time_name).value = (
                new_datetime.strftime("%H") + time_value[2:])

    def _anonymize_datetime(self, dataset, data_element):
        datetime_value = data_element.value
        datetime_format = "%Y%m%d%H"[:len(datetime_value)-2]

        old_datetime = datetime.datetime.strptime(
            datetime_value[:10], datetime_format)
        new_datetime = old_datetime + self.offset

        new_datetime_value = new_datetime.strftime(datetime_format)
        new_datetime_value += datetime_value[len(new_datetime_value):]
        data_element.value = new_datetime_value
