from ..models import AppSettings


class AppSettingsDude:
    def __init__(self):
        """
        Fetch current settings from db and set properties.
        """
        self.app_settings = AppSettings.objects.get(pk=1)
        self.date_format = self._set_date_format()
        self.time_format = self._set_time_format()
        self.datetime_format = self.date_format + ' ' + self.time_format

    def _set_date_format(self):
        """
        Set the current date format
        :param self:
        :return:
        """
        #  set date and time formats
        date_formats = [
            ('%Y-%m-%d', 'YYYY-MM-DD'),
            ('%m-%d-%Y', 'MM-DD-YYYY'),
            ('%d-%m-%Y', 'DD-MM-YYYY')
        ]

        if self.app_settings.date_format is None:
            return '%Y-%m-%d'

        date_format = '%Y-%m-%d'
        for df in date_formats:
            if self.app_settings.date_format == df[1]:
                date_format = df[0]

        return date_format

    def _set_time_format(self):
        """
        Set the current time format
        :return:
        """
        if self.app_settings.time_format == 12:
            return "%-I %p"
        else:
            return "%H:%M"
