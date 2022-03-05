import io

from django.db.models import Q
from django.http import Http404, HttpResponse, FileResponse
from django.template.loader import get_template, render_to_string
from django.utils.translation import gettext as _
import openpyxl

from ...models import FinanceInvoiceItem

from ...modules.graphql_jwt_tools import get_user_by_token


def export_excel_finance_invoices(request, token, date_from, date_until, status, **kwargs):
    """
    Export invoices as Excel
    """
    print(token)
    print(date_from)
    print(date_until)
    print(status)

    user = get_user_by_token(token, request)
    if not user.has_perm('costasiella.view_financeinvoice'):
        raise Http404("Permission denied")


    # iac_dude = InsightAccountClasspassesDude()
    # data = iac_dude.get_classpasses_sold_year_data(year)
    # print(data)

    wb = openpyxl.Workbook(write_only=True)
    ws_header = [
        _('InvoiceID'),
        _('Invoice group'),
        _('Account ID'),
        _('Account Name'),
        _('Date Created'),
        _('Date Due'),
        _('Status'),
        _('Description'),
        _('G/L Account'),
        _('Costcenter'),
        _('Item #'),
        _('Item Name'),
        _('Item Description'),
        _('Qty'),
        _('Price (each)'),
        _('Tax %'),
        _('Tax name'),
        _('Total excl. VAT'),
        _('VAT'),
        _('Total incl. VAT'),
        _('Payment Method'),
        _('Organization Subscription ID'),
        _('Organization Subscription Name'),
        _('Subscription Year'),
        _('Subscription Month'),
    ]

    sheet_title = _('Invoice items').format(
        date_from=date_from,
        date_until=date_until
    )
    ws = wb.create_sheet(sheet_title)
    ws.append(ws_header)

    invoice_items = FinanceInvoiceItem.objects.filter(
        Q(finance_invoice__date_sent__gte=date_from),
        Q(finance_invoice__date_sent__lte=date_until),
    )

    if status != "ALL":
        invoice_items.filter(status=status)

    for invoice_item in invoice_items:
        finance_invoice = invoice_item.finance_invoice

        ws.append([
            finance_invoice.invoice_number
        ])

    # # Create a file-like buffer to receive xlsx data.
    buffer = io.BytesIO()
    wb.save(buffer)

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    filename = "Invoice_items_{date_from}_{date_until}.xlsx".format(
        date_from=date_from,
        date_until=date_until
    )

    return FileResponse(buffer, as_attachment=True, filename=filename)

