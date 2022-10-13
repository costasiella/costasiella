import datetime
import calendar
from decimal import Decimal

from django.utils.translation import gettext as _
from django.db.models import Q, Sum


class InsightRevenueDude:
    def get_data(self, year):
        """
        Add data to a list, easily consumed by the javascript recharts library
        """
        data = []

        data_total = self.get_revenue_total_year(year)
        data_subtotal = self.get_revenue_subtotal_year(year)
        data_tax = self.get_revenue_tax_year(year)

        for i in range(1, 13):
            data.append({
                'month': i,
                'total': data_total[i],
                'subtotal': data_subtotal[i],
                'tax': data_tax[i],
            })

        return data

    def get_data_in_category(self, year, category):
        """
        Add data to a list, easily consumed by the javascript recharts library
        """
        data = []

        data_total = self.get_revenue_total_in_category_for_year(year, category)
        data_subtotal = self.get_revenue_subtotal_in_category_for_year(year, category)
        data_tax = self.get_revenue_tax_in_category_for_year(year, category)

        for i in range(1, 13):
            data.append({
                'month': i + 1,
                'total': data_total[i],
                'subtotal': data_subtotal[i],
                'tax': data_tax[i],
            })

        return data

    @staticmethod
    def get_revenue_total_period(date_from, date_until):
        """
        Return sums of revenue in the given period
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

    @staticmethod
    def get_revenue_in_category_period(date_from, date_until, category):
        """
        Return sums of revenue in the given period
        """
        from ..models import FinanceInvoiceItem

        categories = [
            'SUBSCRIPTIONS',
            'CLASSPASSES',
            'EVENTTICKETS',
            'OTHER'
        ]
        if category not in categories:
            raise Exception(_("Category not one of SUBSCRIPTIONS, CLASSPASSES, EVENTTICKETS or OTHER"))

        # Define basic query set
        sums = FinanceInvoiceItem.objects.filter(
            ~(Q(finance_invoice__status='CANCELLED') | Q(finance_invoice__status='DRAFT')),
            finance_invoice__date_sent__gte=date_from,
            finance_invoice__date_sent__lte=date_until,
        )

        # Add category filter to query set
        if category == 'SUBSCRIPTIONS':
            sums = sums.filter(account_subscription__isnull=False)
        elif category == "CLASSPASSES":
            sums = sums.filter(account_classpass__isnull=False)
        elif category == "EVENTTICKETS":
            sums = sums.filter(account_schedule_event_ticket__isnull=False)
        elif category == "OTHER":
            sums = sums.filter(
                account_subscription__isnull=True,
                account_classpass__isnull=True,
                account_schedule_event_ticket__isnull=True
            )

        sums = sums.aggregate(Sum('total'), Sum('subtotal'), Sum('tax'))

        return sums

    def get_revenue_total_in_category_for_year(self, year, category):
        from collections import OrderedDict

        data = OrderedDict()
        for i in range(1, 13):
            date_from = datetime.date(year, i, 1)
            last_day_month = calendar.monthrange(year, i)[1]
            date_until = datetime.date(year, i, last_day_month)

            revenue_in_month = self.get_revenue_in_category_period(
                date_from, date_until, category
            ).get('total__sum')
            data[i] = revenue_in_month or Decimal(0)

        return data

    def get_revenue_subtotal_in_category_for_year(self, year, category):
        from collections import OrderedDict

        data = OrderedDict()
        for i in range(1, 13):
            date_from = datetime.date(year, i, 1)
            last_day_month = calendar.monthrange(year, i)[1]
            date_until = datetime.date(year, i, last_day_month)

            revenue_in_month = self.get_revenue_in_category_period(
                date_from, date_until, category
            ).get('subtotal__sum')
            data[i] = revenue_in_month or Decimal(0)

        return data

    def get_revenue_tax_in_category_for_year(self, year, category):
        from collections import OrderedDict

        data = OrderedDict()
        for i in range(1, 13):
            date_from = datetime.date(year, i, 1)
            last_day_month = calendar.monthrange(year, i)[1]
            date_until = datetime.date(year, i, last_day_month)

            tax_in_month = self.get_revenue_in_category_period(
                date_from, date_until, category
            ).get('tax__sum')
            data[i] = tax_in_month or Decimal(0)

        return data
