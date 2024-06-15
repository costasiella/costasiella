import datetime
import calendar

from django.utils.translation import gettext as _
from django.db.models import Q


class InsightAccountSubscriptionsDude:
    def get_data(self, year):
        """
        Add data to a list, easily consumed by the javascript recharts library
        """
        data = []

        data_sold = self.get_subscriptions_sold_year_summary_count(year)
        data_stopped = self.get_subscriptions_stopped_year_summary_count(year)
        data_active = self.get_subscriptions_active_year_summary_count(year)
        data_paused = self.get_subscriptions_paused_year_summary_count(year)
        data_blocked = self.get_subscriptions_blocked_year_summary_count(year)

        for i in range(0, 12):
            data.append({
                'month': i + 1,
                'sold': data_sold[i],
                'stopped': data_stopped[i],
                'active': data_active[i],
                'paused': data_paused[i],
                'blocked': data_blocked[i]
            })

        return data

    def get_subscriptions_sold_period_count(self, date_from, date_until):
        """
        Return count of sold (new) subscriptions in a period
        """
        from ..models import AccountSubscription

        count = AccountSubscription.objects.filter(
            date_start__gte=date_from,
            date_start__lte=date_until
        ).count()

        return count

    def get_subscriptions_sold_year_summary_count(self, year):
        """
        Return monthly counts of sold (new) subscriptions
        """
        data = []

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
            date_start__gte=date_from,
            date_start__lte=date_until
        ).order_by("date_start")

        return qs

    def get_subscriptions_sold_year_data(self, year):
        """
        Get subscriptions sold (new) year data
        """
        from collections import OrderedDict

        data = OrderedDict()

        for i in range(1, 13):
            date_from = datetime.date(year, i, 1)
            last_day_month = calendar.monthrange(year, i)[1]
            date_until = datetime.date(year, i, last_day_month)

            subscriptions_sold_in_month = self.get_subscriptions_sold_period_data(date_from, date_until)
            data[i] = subscriptions_sold_in_month

        return data

    def get_subscriptions_stopped_period_count(self, date_from, date_until):
        """
        Return count of stopped (ended) subscriptions in a period
        """
        from ..models import AccountSubscription

        count = AccountSubscription.objects.filter(
            date_end__gte=date_from,
            date_end__lte=date_until
        ).count()

        return count

    def get_subscriptions_stopped_year_summary_count(self, year):
        """
        Return monthly counts of stopped (ended) subscriptions
        """
        data = []

        for i in range(1, 13):
            date_from = datetime.date(year, i, 1)
            last_day_month = calendar.monthrange(year, i)[1]
            date_until = datetime.date(year, i, last_day_month)

            stopped_in_month = self.get_subscriptions_stopped_period_count(date_from, date_until)
            data.append(stopped_in_month)

        return data

    def get_subscriptions_stopped_period_data(self, date_from, date_until):
        """
        Return data list of stopped subscriptions in a period
        """
        from ..models import AccountSubscription

        qs = AccountSubscription.objects.filter(
            date_end__gte=date_from,
            date_end__lte=date_until
        ).order_by("date_end")

        return qs

    def get_subscriptions_stopped_year_data(self, year):
        """
        Get subscriptions stopped (ended) year data
        """
        from collections import OrderedDict

        data = OrderedDict()

        for i in range(1, 13):
            date_from = datetime.date(year, i, 1)
            last_day_month = calendar.monthrange(year, i)[1]
            date_until = datetime.date(year, i, last_day_month)

            subscriptions_stopped_in_month = self.get_subscriptions_stopped_period_data(date_from, date_until)
            data[i] = subscriptions_stopped_in_month

        return data

    def get_subscriptions_active_period_count(self, date_from, date_until):
        """
        Return count of active subscriptions in a period
        """
        from ..models import AccountSubscription

        count = AccountSubscription.objects.filter(
            (Q(date_end__gte=date_from) | Q(date_end__isnull=True)),
            date_start__lte=date_until,
        ).count()

        return count

    def get_subscriptions_active_year_summary_count(self, year):
        """
        Return monthly counts of active passes
        """
        data = []

        for i in range(1, 13):
            date_from = datetime.date(year, i, 1)
            last_day_month = calendar.monthrange(year, i)[1]
            date_until = datetime.date(year, i, last_day_month)

            active_in_month = self.get_subscriptions_active_period_count(date_from, date_until)
            data.append(active_in_month)

        return data

    def get_subscriptions_active_period_data(self, date_from, date_until):
        """
        Return data list of active subscriptions in a period
        """
        from ..models import AccountSubscription

        qs = AccountSubscription.objects.filter(
            (Q(date_end__gte=date_from) | Q(date_end__isnull=True)),
            date_start__lte=date_until,
        ).order_by("date_start")

        return qs

    def get_subscriptions_active_year_data(self, year):
        """
        Get subscriptions active year data
        """
        from collections import OrderedDict

        data = OrderedDict()

        for i in range(1, 13):
            date_from = datetime.date(year, i, 1)
            last_day_month = calendar.monthrange(year, i)[1]
            date_until = datetime.date(year, i, last_day_month)

            subscriptions_active_in_month = self.get_subscriptions_active_period_data(date_from, date_until)
            data[i] = subscriptions_active_in_month

        return data

    ###
    # For the paused it's good to document that pauses are counted as
    # "paused somewhere in the month"
    ###

    def get_subscriptions_paused_period_count(self, date_from, date_until):
        """
        Return count of paused subscriptions in a period
        """
        from ..models import AccountSubscriptionPause

        count = AccountSubscriptionPause.objects.filter(
            (Q(date_end__gte=date_from) | Q(date_end__isnull=True)),
            date_start__lte=date_until,
        ).count()

        return count

    def get_subscriptions_paused_year_summary_count(self, year):
        """
        Return monthly counts of paused subscriptions
        """
        data = []

        for i in range(1, 13):
            date_from = datetime.date(year, i, 1)
            last_day_month = calendar.monthrange(year, i)[1]
            date_until = datetime.date(year, i, last_day_month)

            paused_in_month = self.get_subscriptions_paused_period_count(date_from, date_until)
            data.append(paused_in_month)

        return data

    def get_subscriptions_paused_period_data(self, date_from, date_until):
        """
        Return data list of paused subscriptions in a period
        """
        from ..models import AccountSubscriptionPause

        qs = AccountSubscriptionPause.objects.filter(
            (Q(date_end__gte=date_from) | Q(date_end__isnull=True)),
            date_start__lte=date_until,
        ).order_by("date_start")

        return qs

    def get_subscriptions_paused_year_data(self, year):
        """
        Get subscriptions paused year data
        """
        from collections import OrderedDict

        data = OrderedDict()

        for i in range(1, 13):
            date_from = datetime.date(year, i, 1)
            last_day_month = calendar.monthrange(year, i)[1]
            date_until = datetime.date(year, i, last_day_month)

            subscriptions_paused_in_month = self.get_subscriptions_paused_period_data(date_from, date_until)
            data[i] = subscriptions_paused_in_month

        return data

    ###
    # For the blocked it's good to document that pauses are counted as
    # "blocked somewhere in the month"
    ###

    def get_subscriptions_blocked_period_count(self, date_from, date_until):
        """
        Return count of blocked subscriptions in a period
        """
        from ..models import AccountSubscriptionBlock

        count = AccountSubscriptionBlock.objects.filter(
            (Q(date_end__gte=date_from) | Q(date_end__isnull=True)),
            date_start__lte=date_until,
        ).count()

        return count

    def get_subscriptions_blocked_year_summary_count(self, year):
        """
        Return monthly counts of blocked subscriptions
        """
        data = []

        for i in range(1, 13):
            date_from = datetime.date(year, i, 1)
            last_day_month = calendar.monthrange(year, i)[1]
            date_until = datetime.date(year, i, last_day_month)

            blocked_in_month = self.get_subscriptions_blocked_period_count(date_from, date_until)
            data.append(blocked_in_month)

        return data

    def get_subscriptions_blocked_period_data(self, date_from, date_until):
        """
        Return data list of blocked subscriptions in a period
        """
        from ..models import AccountSubscriptionBlock

        qs = AccountSubscriptionBlock.objects.filter(
            (Q(date_end__gte=date_from) | Q(date_end__isnull=True)),
            date_start__lte=date_until,
        ).order_by("date_start")

        return qs

    def get_subscriptions_blocked_year_data(self, year):
        """
        Get subscriptions blocked year data
        """
        from collections import OrderedDict

        data = OrderedDict()

        for i in range(1, 13):
            date_from = datetime.date(year, i, 1)
            last_day_month = calendar.monthrange(year, i)[1]
            date_until = datetime.date(year, i, last_day_month)

            subscriptions_blocked_in_month = self.get_subscriptions_blocked_period_data(date_from, date_until)
            data[i] = subscriptions_blocked_in_month

        return data
