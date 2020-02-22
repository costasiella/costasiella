import datetime
import calendar

from django.utils.translation import gettext as _
from django.db import models, Sum
from django.db.models import Q



class InsightDataDude:
    def get_classpasses_period_sold_count(date_from, date_until):
        """
        Get count of sold classpasses in a period
        """
        return models.AccountClasspass.objects.filter(
            date_start__gte = date_from,
            date_start__lte = date_until
        ).count()


    def get_classpasses_year_summary_count(year):
        """
        Return monthly counts of sold passes
        """
        data = []

        for i in range(1, 13):
            date_from = datetime.date(year, i, 1)
            date_until = last_day_new = calendar.monthrange(year, i)[1]

            sold_in_month = self.get_classpasses_period_sold_count(date_from, date_until)
            data.append(sold_in_month)

        return data
