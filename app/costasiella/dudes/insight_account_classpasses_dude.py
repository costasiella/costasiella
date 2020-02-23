import datetime
import calendar

from django.utils.translation import gettext as _
from django.db.models import Q


class InsightAccountClasspassesDude:
    def get_classpasses_sold_period_count(self, date_from, date_until):
        """
        Get count of sold classpasses in a period
        """
        from ..models import AccountClasspass

        count = AccountClasspass.objects.filter(
            date_start__gte = date_from,
            date_start__lte = date_until
        ).count()

        print(count)
        return count


    def get_classpasses_sold_year_summary_count(self, year):
        """
        Return monthly counts of sold passes
        """
        data = []

        print(year)

        for i in range(1, 13):
            date_from = datetime.date(year, i, 1)
            last_day_month = calendar.monthrange(year, i)[1]
            date_until = datetime.date(year, i, last_day_month)

            sold_in_month = self.get_classpasses_sold_period_count(date_from, date_until)
            data.append(sold_in_month)

        return data


    def get_classpasses_


    def get_classpasses_sold_year_data(self, year):
        """
        Get classpasses sold year data
        """
