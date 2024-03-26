import calendar
import datetime


class DateToolsDude:
    @staticmethod
    def get_last_day_month(date):
        """
            This function returns the last day of the month as a datetime.date object
        """
        return datetime.date(date.year,
                             date.month,
                             calendar.monthrange(date.year, date.month)[1])


    def get_first_isoweekday_in_first_week_of_year(self, iso_year, iso_weekday):
        """
        Gets the first weekday in ISO week number 1.
        Useful for attendance charts, the week numbers will be the same as in calendars.
        :param iso_year: int - YYYY
        :param iso_weekday: int - 1 - 7
        :return: datetime.date of first weekday in weeknr 1
        """
        return self.iso_to_gregorian(iso_year, 1, iso_weekday)

    def get_first_day_of_next_month_from_date(self, date):
        """
        Returns the first day of the next month of date
        :param date: datetime.date object
        :return: datetime.date object
        """
        last_day_of_month = self.get_last_day_month(date)
        return last_day_of_month + datetime.timedelta(days=1)


    @staticmethod
    def iso_year_start(iso_year):
        """
        The gregorian calendar date of the first day of the given ISO year
        :param iso_year: Int - YYYY
        :return: datetime.date of the first day of the given ISO year
        """
        fourth_jan = datetime.date(iso_year, 1, 4)
        delta = datetime.timedelta(fourth_jan.isoweekday()-1)
        return fourth_jan - delta

    def iso_to_gregorian(self, iso_year, iso_week, iso_day):
        """
        Gregorian calendar date for the given ISO year, week and day
        :param iso_year: Int - YYYY
        :param iso_week: Int - 1 - 53
        :param iso_day: Int - 1 - 7
        :return: datetime.date object for given iso date
        """
        iso_year = int(iso_year)
        iso_week = int(iso_week)
        year_start = self.iso_year_start(iso_year)
        return year_start + datetime.timedelta(days=iso_day-1, weeks=iso_week-1)