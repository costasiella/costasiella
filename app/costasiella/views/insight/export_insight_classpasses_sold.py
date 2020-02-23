import io

from django.utils.translation import gettext as _
from django.utils import timezone
from django.shortcuts import redirect, render
from django.http import Http404, HttpResponse, FileResponse
from django.db.models import Q
from django.template.loader import get_template, render_to_string


# from django.template.loader import render_to_string
# rendered = render_to_string('my_template.html', {'foo': 'bar'})

from ...models import AppSettings
from ...dudes.insight_account_classpasses_dude import InsightAccountClasspassesDude
# from ..modules.gql_tools import require_login_and_permission, get_rid



# Create your views here.
def export_excel_insight_classpasses_sold(request, year):
    """
    Export 

    :param: POST: node_id - FinanceInvoiceNode ID
    """
    import openpyxl
    print("Year:")
    print(year)
    # print(request.POST.node_id)

    iac_dude = InsightAccountClasspassesDude()
    

    
    # finance_invoice, html = invoice_html(node_id)

    # # Create a file-like buffer to receive PDF data.
    # buffer = io.BytesIO()
    # pdf = weasyprint.HTML(string=html).write_pdf(buffer)

    # # FileResponse sets the Content-Disposition header so that browsers
    # # present the option to save the file.
    # buffer.seek(0)

    # filename = _('invoice') + '_' + finance_invoice.invoice_number + '.pdf'

    # return FileResponse(buffer, as_attachment=True, filename=filename)
