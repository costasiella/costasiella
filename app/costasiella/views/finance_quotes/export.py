import io

from django.db.models import Q
from django.http import Http404, HttpResponse, FileResponse
from django.template.loader import get_template, render_to_string
from django.utils.translation import gettext as _
import openpyxl

from ...models import FinanceQuoteItem

from ...modules.graphql_jwt_tools import get_user_from_cookie


def export_excel_finance_quotes(request, date_from, date_until, status, **kwargs):
    """
    Export quotes as Excel
    """
    user = get_user_from_cookie(request)
    if not user.has_perm('costasiella.view_financequote'):
        raise Http404("Permission denied")

    wb = openpyxl.Workbook(write_only=True)
    ws_header = [
        _('QuoteID'),
        _('Quote group'),
        _('B2B relation ID'),
        _('B2B relation Name'),
        _('Account ID'),
        _('Account Name'),
        _('Date Created'),
        _('Date Expiration'),
        _('Status'),
        _('Summary'),
        _('Item #'),
        _('Item Name'),
        _('Item Description'),
        _('Qty'),
        _('Price (each)'),
        _('Tax name'),
        _('Tax %'),
        _('Tax type'),
        _('Total excl. VAT'),
        _('VAT'),
        _('Total incl. VAT'),
        _('G/L Account'),
        _('Cost center')
    ]

    sheet_title = _('Quote items').format(
        date_from=date_from,
        date_until=date_until
    )
    ws = wb.create_sheet(sheet_title)
    ws.append(ws_header)

    quote_items = FinanceQuoteItem.objects.filter(
        Q(finance_quote__date_sent__gte=date_from),
        Q(finance_quote__date_sent__lte=date_until),
    )

    if status != "ALL":
        quote_items.filter(status=status)

    for quote_item in quote_items:
        finance_quote = quote_item.finance_quote
        finance_quote_group = finance_quote.finance_quote_group
        finance_tax_rate = quote_item.finance_tax_rate

        ws.append([
            finance_quote.quote_number,
            finance_quote_group.name,
            finance_quote.business.id if finance_quote.business else "",
            finance_quote.business.name if finance_quote.business else "",
            finance_quote.account.id,
            finance_quote.account.full_name,
            finance_quote.date_sent,
            finance_quote.date_expire,
            finance_quote.status,
            finance_quote.summary,
            quote_item.line_number,
            quote_item.product_name,
            quote_item.description,
            quote_item.quantity,
            quote_item.price,
            finance_tax_rate.name if finance_tax_rate else "",
            finance_tax_rate.percentage if finance_tax_rate else "",
            finance_tax_rate.rate_type if finance_tax_rate else "",
            quote_item.subtotal,
            quote_item.tax,
            quote_item.total,
            quote_item.finance_glaccount.code if quote_item.finance_glaccount else "",
            quote_item.finance_costcenter.code if quote_item.finance_costcenter else "",
        ])

    # # Create a file-like buffer to receive xlsx data.
    buffer = io.BytesIO()
    wb.save(buffer)

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    filename = "Quote_items_{date_from}_{date_until}.xlsx".format(
        date_from=date_from,
        date_until=date_until
    )

    return FileResponse(buffer, as_attachment=True, filename=filename)
