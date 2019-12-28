import io

from django.utils.translation import gettext as _
from django.utils import timezone
from django.shortcuts import redirect, render
from django.http import Http404, HttpResponse, FileResponse
from django.db.models import Q
from django.template.loader import get_template, render_to_string


# from django.template.loader import render_to_string
# rendered = render_to_string('my_template.html', {'foo': 'bar'})

from ..models import AppSettings, FinanceInvoice, FinanceInvoiceGroup, FinanceInvoiceGroupDefault, FinanceInvoiceItem, Organization
from ..modules.gql_tools import require_login_and_permission, get_rid


def invoice_html(node_id):
    """
    Return rendered invoice html template
    """
    rid = get_rid(node_id)
    print(rid)
    finance_invoice = FinanceInvoice.objects.get(id=rid.id)

    if not finance_invoice:
        raise Http404(_("Invoice not found..."))

    app_settings = AppSettings.objects.get(id=1)
    organization = Organization.objects.get(id=100)
    items = FinanceInvoiceItem.objects.filter(
        finance_invoice = finance_invoice
    )

    tax_rates = finance_invoice.tax_rates_amounts()

    print(finance_invoice)
    print(tax_rates)

    template_path = 'system/invoices/export_invoice_pdf.html'
    t = get_template(template_path)
    print(t)
    rendered_template = render_to_string(
        template_path,
        {
            "logo": "logo",
            "studio": {
                "name": "studio name",
            },
            "invoice": finance_invoice,
            "date_sent": finance_invoice.date_sent,
            "organization": organization,
            "items": items,
            "tax_rates": tax_rates,
        }
    )

    return rendered_template


    # permission  = ((auth.has_membership(group_id='Admins') or
    #                 auth.has_permission('read', 'invoices')) or
    #                invoice.get_linked_customer_id() == auth.user.id)

    # if not permission:
    #     return T("Not authorized")

    # html = pdf_template(iID)

    # fname = 'Invoice_' + invoice.invoice.InvoiceID + '.pdf'
    # response.headers['Content-Type']='application/pdf'
    # response.headers['Content-disposition']='attachment; filename=' + fname
    # # return pyfpdf_from_html(html)

    # stream = io.BytesIO()
    # invoice = weasyprint.HTML(string=html).write_pdf(stream)

    # return stream.getvalue()


# Create your views here.
def invoice_pdf(request, node_id):
    """
    Export invoice as PDF

    :param: POST: node_id - FinanceInvoiceNode ID
    """
    import weasyprint
    print("InvoiceID:")
    print(node_id)
    # print(request.POST.node_id)

    html = invoice_html(node_id)

    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()
    pdf = weasyprint.HTML(string=html).write_pdf(buffer)

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename='invoice.pdf')


def invoice_pdf_preview(request, node_id):
    """
    Preview for invoice_pdf

    :param: POST: node_id - FinanceInvoiceNode ID
    """
    print("InvoiceID:")
    print(node_id)
    # print(request.POST.node_id)

    html = invoice_html(node_id)

    return HttpResponse(html)
