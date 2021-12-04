import datetime
import calendar

from django.utils.translation import gettext as _
from django.db.models import Q, Sum


class InsightFinanceTaxSummaryDude:
    def get_tax_rate_summary(self, date_start, date_end):
        """
        Fetch summary of tax rates
        :param date_start:
        :param date_end:
        :return:
        """
        from ..models import FinanceTaxRate

        sum_tax = Sum('invoice_items__tax')
        sum_subtotal = Sum('invoice_items__subtotal')

        qs = FinanceTaxRate.objects.filter(
            invoice_items__finance_invoice__date_sent__gte=date_start,
            invoice_items__finance_invoice__date_sent__lte=date_end,
        ).annotate(sum_tax=sum_tax).annotate(sum_subtotal=sum_subtotal)

        return qs
