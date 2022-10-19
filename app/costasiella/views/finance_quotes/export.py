import io

from django.db.models import Q
from django.http import Http404, HttpResponse, FileResponse
from django.template.loader import get_template, render_to_string
from django.utils.translation import gettext as _
import openpyxl

from ...models import AppSettings, FinanceQuote, FinanceQuoteItem, Organization

from ...modules.graphql_jwt_tools import get_user_from_cookie
from ...modules.gql_tools import require_login_and_permission, get_rid


def export_excel_finance_quotes(request, date_from, date_until, status, **kwargs):
    """
    Export quote items as Excel
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


def _verifiy_permission_or_account(request, finance_quote, **kwargs):
    """
    :param request:
    :param finance_quote:
    :return:
    """
    user = get_user_from_cookie(request, **kwargs)

    if not user:
        return False

    if user.has_perm('costasiella.view_financequote') or finance_quote.account == user:
        return True
    else:
        return False


def quote_html(node_id):
    """
    Return rendered quote html template
    """
    from ...dudes import SystemSettingDude

    rid = get_rid(node_id)
    finance_quote = FinanceQuote.objects.get(id=rid.id)

    if not finance_quote:
        raise Http404(_("Quote not found..."))

    system_settings_dude = SystemSettingDude()
    currency_symbol = system_settings_dude.get("finance_currency_symbol") or "€"

    app_settings = AppSettings.objects.get(id=1)
    organization = Organization.objects.get(id=100)
    # Use the invoice logo for quotes as well
    logo_url = organization.logo_invoice.url if organization.logo_invoice else ""
    items = FinanceQuoteItem.objects.filter(
        finance_quote=finance_quote
    )
    tax_rates = finance_quote.tax_rates_amounts()

    template_path = 'system/quotes/export_quote_pdf.html'
    t = get_template(template_path)

    rendered_template = render_to_string(
        template_path,
        {
            "currency_symbol": currency_symbol,
            "logo_url": logo_url,
            "quote": finance_quote,
            "date_sent": finance_quote.date_sent,
            "organization": organization,
            "items": items,
            "tax_rates": tax_rates,
        }
    )

    return [finance_quote, rendered_template]


# Create your views here.
def quote_pdf(request, node_id, **kwargs):
    """
    Export quote as PDF

    :param: POST: node_id - FinanceQuoteNode ID
    """
    import weasyprint

    finance_quote, html = quote_html(node_id)
    if not _verifiy_permission_or_account(request, finance_quote, **kwargs):
        raise Http404(_("Quote not found..."))

    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()
    # Write pdf to memory buffer
    weasyprint.HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(buffer)

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)

    filename = _('quote') + '_' + finance_quote.quote_number + '.pdf'

    return FileResponse(buffer, as_attachment=True, filename=filename)


def quote_pdf_preview(request, node_id):
    """
    Preview for quote_pdf

    :param: POST: node_id - FinanceQuoteNode ID
    """

    finance_quote, html = quote_html(node_id)
    if not _verifiy_permission_or_account(request, finance_quote):
        raise Http404(_("Quote not found..."))

    return HttpResponse(html)
