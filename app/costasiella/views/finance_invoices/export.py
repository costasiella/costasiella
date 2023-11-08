import io

from django.db.models import Q
from django.http import Http404, HttpResponse, FileResponse
from django.template.loader import get_template, render_to_string
from django.utils.translation import gettext as _
import openpyxl

from ...models import FinanceInvoiceItem

from ...modules.graphql_jwt_tools import get_user_from_cookie


def export_excel_finance_invoices(request, date_from, date_until, status, **kwargs):
    """
    Export invoices as Excel
    """
    user = get_user_from_cookie(request)
    if not user.has_perm('costasiella.view_financeinvoice'):
        raise Http404("Permission denied")

    wb = openpyxl.Workbook(write_only=True)
    ws_header = [
        _('InvoiceID'),
        _('Invoice group'),
        _('B2B relation ID'),
        _('B2B relation Name'),
        _('Account ID'),
        _('Account Name'),
        _('Date Created'),
        _('Date Due'),
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
        _('Cost center'),
        _('Payment Method'),
        _('Account Subscription ID'),
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
        invoice_items = invoice_items.filter(
            finance_invoice__status=status
        )

    for invoice_item in invoice_items:
        finance_invoice = invoice_item.finance_invoice
        finance_invoice_group = finance_invoice.finance_invoice_group
        finance_tax_rate = invoice_item.finance_tax_rate

        account_subscription_id = ""
        organization_subscription_name = ""
        if invoice_item.account_subscription:
            account_subscription_id = invoice_item.account_subscription.id
            organization_subscription_name = invoice_item.account_subscription.organization_subscription.name

        ws.append([
            finance_invoice.invoice_number,
            finance_invoice_group.name,
            finance_invoice.business.id if finance_invoice.business else "",
            finance_invoice.business.name if finance_invoice.business else "",
            finance_invoice.account.id if finance_invoice.account else "",
            finance_invoice.account.full_name if finance_invoice.account else "",
            finance_invoice.date_sent,
            finance_invoice.date_due,
            finance_invoice.status,
            finance_invoice.summary,
            invoice_item.line_number,
            invoice_item.product_name,
            invoice_item.description,
            invoice_item.quantity,
            invoice_item.price,
            finance_tax_rate.name if finance_tax_rate else "",
            finance_tax_rate.percentage if finance_tax_rate else "",
            finance_tax_rate.rate_type if finance_tax_rate else "",
            invoice_item.subtotal,
            invoice_item.tax,
            invoice_item.total,
            invoice_item.finance_glaccount.code if invoice_item.finance_glaccount else "",
            invoice_item.finance_costcenter.code if invoice_item.finance_costcenter else "",
            finance_invoice.finance_payment_method.name if finance_invoice.finance_payment_method else "",
            account_subscription_id,
            organization_subscription_name,
            invoice_item.subscription_year or "",
            invoice_item.subscription_month or ""
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

