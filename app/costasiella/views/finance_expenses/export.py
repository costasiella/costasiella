import io

from django.db.models import Q
from django.http import Http404, HttpResponse, FileResponse
from django.template.loader import get_template, render_to_string
from django.utils.translation import gettext as _
import openpyxl

from ...models import AppSettings, FinanceExpense

from ...modules.graphql_jwt_tools import get_user_from_cookie


def export_excel_finance_expenses(request, date_from, date_until, **kwargs):
    """
    Export expenses as Excel
    """
    user = get_user_from_cookie(request)
    if not user.has_perm('costasiella.view_financeexpense'):
        raise Http404("Permission denied")

    wb = openpyxl.Workbook(write_only=True)
    ws_header = [
        _('Expense #'),
        _('Date'),
        _('Summary'),
        _('Description'),
        _('Amount'),
        _('Tax'),
        _('Subtotal'),
        _('Percentage'),
        _('Total Amount'),
        _('Total Tax'),
        _('Total'),
        _('Supplier'),
        _('GLAccount name'),
        _('GLAccount code'),
        _('Cost Center name'),
        _('Cost Center code'),
    ]

    sheet_title = _('Expenses').format(
        date_from=date_from,
        date_until=date_until
    )
    ws = wb.create_sheet(sheet_title)
    ws.append(ws_header)

    finance_expenses = FinanceExpense.objects.filter(
        Q(date__gte=date_from),
        Q(date__lte=date_until),
    )

    # if status != "ALL":
    #     invoice_items.filter(status=status)

    for finance_expense in finance_expenses:
        supplier = finance_expense.supplier
        finance_glaccount = finance_expense.finance_glaccount
        finance_costcenter = finance_expense.finance_costcenter

        ws.append([
            finance_expense.id,
            finance_expense.date,
            finance_expense.summary,
            finance_expense.description,
            finance_expense.amount,
            finance_expense.tax,
            finance_expense.subtotal,
            finance_expense.percentage,
            finance_expense.total_amount,
            finance_expense.total_tax,
            finance_expense.total,
            supplier.name if supplier else "",
            finance_glaccount.name if finance_glaccount else "",
            finance_glaccount.code if finance_glaccount else "",
            finance_costcenter.name if finance_costcenter else "",
            finance_costcenter.code if finance_costcenter else "",
        ])

    # # Create a file-like buffer to receive xlsx data.
    buffer = io.BytesIO()
    wb.save(buffer)

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    filename = "Expenses_{date_from}_{date_until}.xlsx".format(
        date_from=date_from,
        date_until=date_until
    )

    return FileResponse(buffer, as_attachment=True, filename=filename)
