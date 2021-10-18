import io

from django.utils.translation import gettext as _
from django.utils import timezone
from django.shortcuts import redirect, render
from django.http import Http404, StreamingHttpResponse, FileResponse
from django.db.models import Q
from django.template.loader import get_template, render_to_string

import openpyxl

# from django.template.loader import render_to_string
# rendered = render_to_string('my_template.html', {'foo': 'bar'})

from ...models import Account


from calendar import timegm
from datetime import datetime

import django
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

# Django-graphql-jwt imports begin
from ...modules.graphql_jwt_tools import get_user_by_token
# Django-graphql-jwt imports end


def export_account_data(request, token, **kwargs):
    """
    Export account data

    :param: POST: token - JWT access token
    """
    user = get_user_by_token(token, request)
    print(user)
    if not user:
        raise Http404(_("Please sign in to export your account data."))

    # Create a new workbook to hold the worksheets containing data
    wb = openpyxl.workbook.Workbook(write_only=True)
    wb = _add_worksheet_account(user, wb)

    #TODO Add functions to add sheets to the workbook; 1 per table

    # # Create a file-like buffer to receive XLSX data.
    buffer = io.BytesIO()
    wb.save(buffer)

    buffer.seek(0)
    account_name = user.full_name.replace(" ", "_")
    filename = _('account_data') + '_' + account_name + ".xlsx"

    return FileResponse(buffer, as_attachment=True, filename=filename)


def _add_worksheet_account(account, wb):
    """
    Add Account sheet to workbook data export
    :param account: models.Account object
    :param wb: openpyxl.workbook.Workbook object
    :return: openpyxl.workbook.Workbook object (appended with Account worksheet)
    """
    ws = wb.create_sheet("Account")

    # Write header
    header = [
        "First name",
        "Last name",
        "Email",
        "Gender",
        "Date of birth",
        "Address",
        "Postcode",
        "City",
        "Country",
        "Phone",
        "Mobile",
        "Emergency",
        "Key nr",
        "Last login",
    ]
    ws.append(header)

    # Write data
    data = [
        account.first_name,
        account.last_name,
        account.email,
        account.gender,
        account.date_of_birth,
        account.address,
        account.postcode,
        account.city,
        account.country,
        account.phone,
        account.mobile,
        account.emergency,
        account.key_number,
        account.last_login,
    ]
    ws.append(data)

    return wb
