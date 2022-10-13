import datetime
import calendar

from django.utils.translation import gettext as _
from django.db.models import Q


class InsightAccountClasspassesDude:
    def get_data(self, year):
        """
        Add data to a list, easily consumed by the javascript recharts library
        """
        data = []

        data_sold = self.get_classpasses_sold_year_summary_count(year)
        data_active = self.get_classpasses_active_year_summary_count(year)

        for i in range(0, 12):
            data.append({
                'month': i + 1,
                'sold': data_sold[i],
                'active': data_active[i]
            })

        return data

    def get_classpasses_sold_period_count(self, date_from, date_until):
        """
        Return count of sold classpasses in a period
        """
        from ..models import AccountClasspass

        count = AccountClasspass.objects.filter(
            date_start__gte=date_from,
            date_start__lte=date_until
        ).count()

        return count

    def get_classpasses_sold_year_summary_count(self, year):
        """
        Return monthly counts of sold passes
        """
        data = []

        for i in range(1, 13):
            date_from = datetime.date(year, i, 1)
            last_day_month = calendar.monthrange(year, i)[1]
            date_until = datetime.date(year, i, last_day_month)

            sold_in_month = self.get_classpasses_sold_period_count(date_from, date_until)
            data.append(sold_in_month)

        return data

    def get_classpasses_sold_period_data(self, date_from, date_until):
        """
        Return data list of sold classpasses in a period
        """
        from ..models import AccountClasspass

        qs = AccountClasspass.objects.filter(
            date_start__gte = date_from,
            date_start__lte = date_until
        ).order_by("date_start")

        return qs

    def get_classpasses_sold_year_data(self, year):
        """
        Get classpasses sold year data
        """
        from collections import OrderedDict

        data = OrderedDict()

        for i in range(1, 13):
            date_from = datetime.date(year, i, 1)
            last_day_month = calendar.monthrange(year, i)[1]
            date_until = datetime.date(year, i, last_day_month)

            classpasses_sold_in_month = self.get_classpasses_sold_period_data(date_from, date_until)
            data[i] = classpasses_sold_in_month

        return data

    def get_classpasses_active_period_count(self, date_from, date_until):
        """
        Return count of active classpasses in a period
        """
        from ..models import AccountClasspass

        count = AccountClasspass.objects.filter(
            date_start__lte = date_until,
            date_end__gte = date_from
        ).count()

        return count

    def get_classpasses_active_year_summary_count(self, year):
        """
        Return monthly counts of active passes
        """
        data = []

        for i in range(1, 13):
            date_from = datetime.date(year, i, 1)
            last_day_month = calendar.monthrange(year, i)[1]
            date_until = datetime.date(year, i, last_day_month)

            sold_in_month = self.get_classpasses_active_period_count(date_from, date_until)
            data.append(sold_in_month)

        return data

    def get_classpasses_active_period_data(self, date_from, date_until):
        """
        Return data list of active classpasses in a period
        """
        from ..models import AccountClasspass

        qs = AccountClasspass.objects.filter(
            date_start__lte = date_until,
            date_end__gte = date_from
        ).order_by("date_start")

        return qs

    def get_classpasses_active_year_data(self, year):
        """
        Get classpasses active year data
        """
        from collections import OrderedDict

        data = OrderedDict()

        for i in range(1, 13):
            date_from = datetime.date(year, i, 1)
            last_day_month = calendar.monthrange(year, i)[1]
            date_until = datetime.date(year, i, last_day_month)

            classpasses_active_in_month = self.get_classpasses_active_period_data(date_from, date_until)
            data[i] = classpasses_active_in_month

        return data
