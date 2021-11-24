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

    def get_first_day_of_week_of_year(self, year, iso_weekday):
        """
        eg. Get the first monday of the year
        :param weekday: iso_weekday (1 = Monday, 7 = Sunday)
        :param year: int - year
        :return: datetime.date
        """
        return self.iso_to_gregorian(year, 1, iso_weekday)

    @staticmethod
    def iso_year_start(iso_year):
        """
        The gregorian calendar date of the first day of the given ISO year
        :param iso_year: int
        :return: datetime.date
        """
        fourth_jan = datetime.date(iso_year, 1, 4)
        delta = datetime.timedelta(fourth_jan.isoweekday() - 1)
        return fourth_jan - delta

    @staticmethod
    def iso_to_gregorian(iso_year, iso_week, iso_weekday):
        """
        Gregorian calendar date for the given ISO year, week and day
        :param iso_year: int
        :param iso_week: int
        :param iso_day: int (1-7)
        :return: datetime.date
        """
        iso_year = int(iso_year)
        iso_week = int(iso_week)
        year_start = iso_year_start(iso_year)

        return year_start + datetime.timedelta(days=iso_weekday-1, weeks=iso_week-1)