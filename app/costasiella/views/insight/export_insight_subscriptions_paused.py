import io

from django.utils.translation import gettext as _
from django.http import Http404, HttpResponse, FileResponse

from ...modules.graphql_jwt_tools import get_user_from_cookie
from ...dudes import InsightAccountSubscriptionsDude


# Create your views here.
def export_excel_insight_subscriptions_paused(request, year):
    """
    Export 

    :param: POST: year: int year (yyyy)
    """
    import openpyxl

    user = get_user_from_cookie(request)
    if not user.has_perm('costasiella.view_insight'):
        raise Http404("Permission denied")

    ias_dude = InsightAccountSubscriptionsDude()
    data = ias_dude.get_subscriptions_paused_year_data(year)

    wb = openpyxl.workbook.Workbook(write_only=True)
    ws_header = [
        _("Relation"),
        _("Email"),
        _("Subscription"),
        _("Start"),
        _("End"),
        _("Pause start"),
        _("Pause end"),
        _("Pause description"),
    ]

    for month in range(1, 13):
        month_data = data[month]
        ws = wb.create_sheet(title=_(str(year) + "-" + str(month)))
        ws.append(ws_header)

        for account_subscription_pause in month_data:
            subscription = account_subscription_pause.account_subscription
            data_list = [
                subscription.account.full_name,
                subscription.account.email,
                subscription.organization_subscription.name,
                subscription.date_start,
                subscription.date_end,
                account_subscription_pause.date_start,
                account_subscription_pause.date_end,
                account_subscription_pause.description,
            ]

            ws.append(data_list)

    # # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()
    wb.save(buffer)

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)

    filename = _('subscriptions_paused') + '_' + str(year) + '.xlsx'

    return FileResponse(buffer, as_attachment=True, filename=filename)
