from django.utils.translation import gettext as _
from django.utils import timezone
from django.shortcuts import redirect, render
from django.http import Http404, HttpResponse
from django.db.models import Q
from django.template.loader import get_template, render_to_string


# from django.template.loader import render_to_string
# rendered = render_to_string('my_template.html', {'foo': 'bar'})

from ..models import FinanceInvoice, FinanceInvoiceGroup, FinanceInvoiceGroupDefault, FinanceInvoiceItem
from ..modules.gql_tools import require_login_and_permission, get_rid


# Create your views here.
def invoice_pdf(request, node_id):
    """
    Export invoice as PDF

    :param: POST: node_id - FinanceInvoiceNode ID
    """
    print("InvoiceID:")
    print(node_id)
    # print(request.POST.node_id)

    rid = get_rid(node_id)
    print(rid)
    finance_invoice = FinanceInvoice.objects.filter(id=rid.id).first()

    print(finance_invoice)


    template_path = 'system/invoices/export_invoice_pdf.html'
    t = get_template(template_path)
    print(t)
    rendered_template = render_to_string(template_path)

    return HttpResponse(rendered_template)


def invoice_pdf_preview(request, node_id):
    """
    Preview for invoice_pdf

    :param: POST: node_id - FinanceInvoiceNode ID
    """
    print("InvoiceID:")
    print(node_id)
    # print(request.POST.node_id)

    rid = get_rid(node_id)
    print(rid)
    finance_invoice = FinanceInvoice.objects.get(id=rid.id)

    if not finance_invoice:
        raise Http404(_("Invoice not found..."))

    print(finance_invoice)


    template_path = 'system/invoices/export_invoice_pdf.html'
    t = get_template(template_path)
    print(t)
    rendered_template = render_to_string(template_path)

    return HttpResponse(rendered_template)


    # qs = OrganizationDocument.objects.filter(
    #     Q(document_type = "TERMS_AND_CONDITIONS") &
    #     Q(date_start__lte = today) &
    #     (Q(date_end__gte = today) | Q(date_end__isnull = True))           
    # )

    # if qs.exists():
    #     document = qs.first()
    #     return redirect(document.document.url)
    # else: 
    #     raise Http404(_("File not found..."))
