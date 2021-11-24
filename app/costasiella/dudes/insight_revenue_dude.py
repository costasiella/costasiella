import datetime
import calendar
from decimal import Decimal

from django.utils.translation import gettext as _
from django.db.models import Q, Sum


class InsightRevenueDude:
    def get_revenue_total_period(self, date_from, date_until):
        """
        Return count of sold (new) subscriptions in a period
        """
        from ..models import FinanceInvoice

        # sums = FinanceOrderItem.objects.filter(finance_order=self).aggregate(Sum('subtotal'), Sum('tax'), Sum('total'))
        #
        # self.subtotal = sums['subtotal__sum'] or 0
        # self.tax = sums['tax__sum'] or 0
        # self.total = sums['total__sum'] or 0

        sums = FinanceInvoice.objects.filter(
            ~(Q(status='CANCELLED') | Q(status='DRAFT')),
            date_sent__gte=date_from,
            date_sent__lte=date_until,

        ).aggregate(Sum('total'), Sum('subtotal'), Sum('tax'))

        print(sums)

        return sums

    def get_revenue_total_year(self, year):
        from collections import OrderedDict

        data = OrderedDict()
        for i in range(1, 13):
            date_from = datetime.date(year, i, 1)
            last_day_month = calendar.monthrange(year, i)[1]
            date_until = datetime.date(year, i, last_day_month)

            revenue_in_month = self.get_revenue_total_period(date_from, date_until).get('total__sum')
            data[i] = revenue_in_month or Decimal(0)

        return data

    def get_revenue_subtotal_year(self, year):
        from collections import OrderedDict

        data = OrderedDict()
        for i in range(1, 13):
            date_from = datetime.date(year, i, 1)
            last_day_month = calendar.monthrange(year, i)[1]
            date_until = datetime.date(year, i, last_day_month)

            revenue_in_month = self.get_revenue_total_period(date_from, date_until).get('subtotal__sum')
            data[i] = revenue_in_month or Decimal(0)

        return data

    def get_revenue_tax_year(self, year):
        from collections import OrderedDict

        data = OrderedDict()
        for i in range(1, 13):
            date_from = datetime.date(year, i, 1)
            last_day_month = calendar.monthrange(year, i)[1]
            date_until = datetime.date(year, i, last_day_month)

            tax_in_month = self.get_revenue_total_period(date_from, date_until).get('tax__sum')
            data[i] = tax_in_month or Decimal(0)

        return data

    #
    #
    # def get_subscriptions_sold_year_summary_count(self, year):
    #     """
    #     Return monthly counts of sold (new) subscriptions
    #     """
    #     data = []
    #
    #     print(year)
    #
    #     for i in range(1, 13):
    #         date_from = datetime.date(year, i, 1)
    #         last_day_month = calendar.monthrange(year, i)[1]
    #         date_until = datetime.date(year, i, last_day_month)
    #
    #         sold_in_month = self.get_subscriptions_sold_period_count(date_from, date_until)
    #         data.append(sold_in_month)
    #
    #     return data
    #
    #
    # def get_subscriptions_sold_period_data(self, date_from, date_until):
    #     """
    #     Return data list of sold (new) subscriptions in a period
    #     """
    #     from ..models import AccountSubscription
    #
    #     qs = AccountSubscription.objects.filter(
    #         date_start__gte = date_from,
    #         date_start__lte = date_until
    #     ).order_by("date_start")
    #
    #     return qs
    #
    #
    # def get_subscriptions_sold_year_data(self, year):
    #     """
    #     Get subscriptions sold (new) year data
    #     """
    #     from collections import OrderedDict
    #
    #     data = OrderedDict()
    #
    #     print(year)
    #
    #     for i in range(1, 13):
    #         date_from = datetime.date(year, i, 1)
    #         last_day_month = calendar.monthrange(year, i)[1]
    #         date_until = datetime.date(year, i, last_day_month)
    #
    #         subscriptions_sold_in_month = self.get_subscriptions_sold_period_data(date_from, date_until)
    #         data[i] = subscriptions_sold_in_month
    #
    #         # print(data)
    #
    #     return data
    #
    #
    # def get_subscriptions_active_period_count(self, date_from, date_until):
    #     """
    #     Return count of active subscriptions in a period
    #     """
    #     from ..models import AccountSubscription
    #
    #     count = AccountSubscription.objects.filter(
    #         (Q(date_end__gte = date_from) | Q(date_end__isnull=True)),
    #         date_start__lte = date_until,
    #     ).count()
    #
    #     print(count)
    #     return count
    #
    #
    # def get_subscriptions_active_year_summary_count(self, year):
    #     """
    #     Return monthly counts of active passes
    #     """
    #     data = []
    #
    #     print(year)
    #
    #     for i in range(1, 13):
    #         date_from = datetime.date(year, i, 1)
    #         last_day_month = calendar.monthrange(year, i)[1]
    #         date_until = datetime.date(year, i, last_day_month)
    #
    #         sold_in_month = self.get_subscriptions_active_period_count(date_from, date_until)
    #         data.append(sold_in_month)
    #
    #     return data
    #
    #
    # def get_subscriptions_active_period_data(self, date_from, date_until):
    #     """
    #     Return data list of active subscriptions in a period
    #     """
    #     from ..models import AccountSubscription
    #
    #     qs = AccountSubscription.objects.filter(
    #         (Q(date_end__gte = date_from) | Q(date_end__isnull=True)),
    #         date_start__lte = date_until,
    #     ).order_by("date_start")
    #
    #     return qs
    #
    #
    # def get_subscriptions_active_year_data(self, year):
    #     """
    #     Get subscriptions active year data
    #     """
    #     from collections import OrderedDict
    #
    #     data = OrderedDict()
    #
    #     print(year)
    #
    #     for i in range(1, 13):
    #         date_from = datetime.date(year, i, 1)
    #         last_day_month = calendar.monthrange(year, i)[1]
    #         date_until = datetime.date(year, i, last_day_month)
    #
    #         subscriptions_active_in_month = self.get_subscriptions_active_period_data(date_from, date_until)
    #         data[i] = subscriptions_active_in_month
    #
    #         # print(data)
    #
    #     return data
