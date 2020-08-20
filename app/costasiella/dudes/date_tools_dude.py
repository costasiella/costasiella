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
