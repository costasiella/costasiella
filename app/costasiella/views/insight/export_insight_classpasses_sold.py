import io

from django.utils.translation import gettext as _
from django.utils import timezone
from django.shortcuts import redirect, render
from django.http import Http404, HttpResponse, FileResponse
from django.db.models import Q
from django.template.loader import get_template, render_to_string


# from django.template.loader import render_to_string
# rendered = render_to_string('my_template.html', {'foo': 'bar'})
import jwt
from .jwt_settings import jwt_settings

from ...models import AppSettings
from ...dudes.insight_account_classpasses_dude import InsightAccountClasspassesDude
# from ..modules.gql_tools import require_login_and_permission, get_rid



# Create your views here.
def export_excel_insight_classpasses_sold(request, year, token):
    """
    Export 
    
    :param: POST: year: int year (yyyy)
    """
    import openpyxl
    print("Year:")
    print(year)
    # print(request.POST.node_id)

    user = get_user_by_token(token, request)
    if not user.has_perm('costasiella.view_insight'):
        raise Http404("Permission denied")

    iac_dude = InsightAccountClasspassesDude()
    data = iac_dude.get_classpasses_sold_year_data(year)
    print(data)

    wb = openpyxl.Workbook(write_only=True)
    ws_header = [
        _("Relation"),
        _("Classpass"),
        _("Start"),
        _("Expiration"),
        _("Price")
    ]

    for month in range(1, 13):
        month_data = data[month]
        print(month_data)
        print(month)
        ws = wb.create_sheet(title=str(year) + "-" + str(month))
        ws.append(ws_header)

        for classpass in month_data:
            data_list = [
                classpass.account.full_name,
                classpass.organization_classpass.name,
                classpass.date_start,
                classpass.date_end,
                classpass.organization_classpass.price
            ]

            ws.append(data_list)

    # # Create a file-like buffer to receive xlsx data.
    buffer = io.BytesIO()
    wb.save(buffer)

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    filename = _('classpasses_sold') + '_' + str(year) + '.xlsx'

    return FileResponse(buffer, as_attachment=True, filename=filename)


### Below is a lot of code from django-graphql-jwt.
"""
We probably don't need it, but for some reason the middleware doesn't seem to pass users properly with the current 
versions. So it can be here for now, until it's fixed upstream.
Everything below here can be deleted again once request.user works again. 
"""


def get_user_by_token(token, context=None):
    payload = get_payload(token, context)
    return get_user_by_payload(payload)

def get_payload(token, context=None):
    try:
        payload = jwt_settings.JWT_DECODE_HANDLER(token, context)
    except jwt.ExpiredSignature:
        raise exceptions.JSONWebTokenExpired()
    except jwt.DecodeError:
        raise exceptions.JSONWebTokenError(_('Error decoding signature'))
    except jwt.InvalidTokenError:
        raise exceptions.JSONWebTokenError(_('Invalid token'))
    return payload

def get_user_by_payload(payload):
    username = jwt_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER(payload)

    if not username:
        raise exceptions.JSONWebTokenError(_('Invalid payload'))

    user = jwt_settings.JWT_GET_USER_BY_NATURAL_KEY_HANDLER(username)

    if user is not None and not getattr(user, 'is_active', True):
        raise exceptions.JSONWebTokenError(_('User is disabled'))
    return user
