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
from ...dudes import InsightAccountSubscriptionsDude


# Create your views here.
def export_excel_insight_subscriptions_active(request, year):
    """
    Export 

    :param: POST: year: int year (yyyy)
    """
    import openpyxl
    print("Year:")
    print(year)
    # print(request.POST.node_id)

    ias_dude = InsightAccountSubscriptionsDude()
    data = ias_dude.get_subscriptions_active_year_data(year)
    print(data)

    wb = openpyxl.workbook.Workbook(write_only=True)
    ws_header = [
        _("Relation"),
        _("Subscription"),
        _("Start"),
        _("Expiration")
    ]

    for month in range(1, 13):
        month_data = data[month]
        print(month_data)
        print(month)
        ws = wb.create_sheet(title=_(str(year) + "-" + str(month)))
        ws.append(ws_header)

        for subscription in month_data:
            data_list = [
                subscription.account.full_name,
                subscription.organization_subscription.name,
                subscription.date_start,
                subscription.date_end
            ]

            ws.append(data_list)

    # # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()
    wb.save(buffer)


    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)

    filename = _('subscriptions_active') + '_' + str(year) + '.xlsx'

    return FileResponse(buffer, as_attachment=True, filename=filename)
