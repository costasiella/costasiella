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

        sums = FinanceInvoice.objects.filter(
            ~(Q(status='CANCELLED') | Q(status='DRAFT')),
            date_sent__gte=date_from,
            date_sent__lte=date_until,

        ).aggregate(Sum('total'), Sum('subtotal'), Sum('tax'))

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
