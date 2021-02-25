import datetime


def next_weekday(date, isoweekday):
    """ Return next weekday after given date 
    :param: weekday : int 0 - 6
    """
    days_ahead = isoweekday - date.isoweekday()
    if days_ahead <= 1: # Target day already happened this week
        days_ahead += 7
    return date + datetime.timedelta(days_ahead)
