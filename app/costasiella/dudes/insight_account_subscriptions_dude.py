import datetime
import calendar

from django.utils.translation import gettext as _
from django.db.models import Q


class InsightAccountSubscriptionsDude:
    def get_subscriptions_sold_period_count(self, date_from, date_until):
        """
        Return count of sold (new) subscriptions in a period
        """
        from ..models import AccountSubscription

        count = AccountSubscription.objects.filter(
            date_start__gte = date_from,
            date_start__lte = date_until
        ).count()

        print(count)
        return count


    def get_subscriptions_sold_year_summary_count(self, year):
        """
        Return monthly counts of sold (new) subscriptions
        """
        data = []

        print(year)

        for i in range(1, 13):
            date_from = datetime.date(year, i, 1)
            last_day_month = calendar.monthrange(year, i)[1]
            date_until = datetime.date(year, i, last_day_month)

            sold_in_month = self.get_subscriptions_sold_period_count(date_from, date_until)
            data.append(sold_in_month)

        return data


    def get_subscriptions_sold_period_data(self, date_from, date_until):
        """
        Return data list of sold (new) subscriptions in a period
        """
        from ..models import AccountSubscription

        qs = AccountSubscription.objects.filter(
            date_start__gte = date_from,
            date_start__lte = date_until
        ).order_by("date_start")

        return qs


    def get_subscription_sold_year_data(self, year):
        """
        Get subscriptions sold (new) year data
        """
        from collections import OrderedDict

        data = OrderedDict()

        print(year)

        for i in range(1, 13):
            date_from = datetime.date(year, i, 1)
            last_day_month = calendar.monthrange(year, i)[1]
            date_until = datetime.date(year, i, last_day_month)

            subscriptions_sold_in_month = self.get_subscriptions_sold_period_data(date_from, date_until)
            data[i] = subscriptions_sold_in_month

            # print(data)

        return data


    def get_subscriptions_active_period_count(self, date_from, date_until):
        """
        Return count of active subscriptions in a period
        """
        from ..models import AccountSubscription

        count = AccountSubscription.objects.filter(
            date_start__lte = date_until,
            (Q(date_end__gte = date_from) | Q(date_end__isnull=True))
        ).count()

        print(count)
        return count


    def get_subscriptions_active_year_summary_count(self, year):
        """
        Return monthly counts of active passes
        """
        data = []

        print(year)

        for i in range(1, 13):
            date_from = datetime.date(year, i, 1)
            last_day_month = calendar.monthrange(year, i)[1]
            date_until = datetime.date(year, i, last_day_month)

            sold_in_month = self.get_subscriptions_active_period_count(date_from, date_until)
            data.append(sold_in_month)

        return data


    def get_subscriptions_active_period_data(self, date_from, date_until):
        """
        Return data list of active subscriptions in a period
        """
        from ..models import AccountSubscription

        qs = AccountSubscription.objects.filter(
            date_start__lte = date_until,
            (Q(date_end__gte = date_from) | Q(date_end__isnull=True))
        ).order_by("date_start")

        return qs


    def get_subscriptions_active_year_data(self, year):
        """
        Get subscriptions active year data
        """
        from collections import OrderedDict

        data = OrderedDict()

        print(year)

        for i in range(1, 13):
            date_from = datetime.date(year, i, 1)
            last_day_month = calendar.monthrange(year, i)[1]
            date_until = datetime.date(year, i, last_day_month)

            subscriptions_active_in_month = self.get_subscriptions_active_period_data(date_from, date_until)
            data[i] = subscriptions_active_in_month

            # print(data)

        return data
