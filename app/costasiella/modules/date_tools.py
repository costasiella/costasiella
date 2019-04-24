import datetime
import calendar

def last_day_month(date):
    """
    Returns last day of month for date
    """
    return calendar.monthrange(date.year, date.month)[1]