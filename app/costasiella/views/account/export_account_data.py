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
    wb = _add_worksheet_account_accepted_documents(user, wb)
    wb = _add_worksheet_account_bank_account(user, wb)
    wb = _add_worksheet_account_bank_account_mandate(user, wb)

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
        "Joined",
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
        account.date_joined.replace(tzinfo=None),
        account.last_login.replace(tzinfo=None) if account.last_login else "",
    ]
    ws.append(data)

    return wb


def _add_worksheet_account_accepted_documents(account, wb):
    """
    Add Account accepted documents sheet to workbook data export
    :param account: models.Account object
    :param wb: openpyxl.workbook.Workbook object
    :return: openpyxl.workbook.Workbook object (appended with Account worksheet)
    """
    ws = wb.create_sheet("Accepted documents")

    # Write header
    header = [
        "Document",
        "Version",
        "From IP",
        "On"
    ]
    ws.append(header)

    for accepted_document in account.accepted_documents.all():
        # Write data
        data = [
            accepted_document.document.document_type,
            accepted_document.document.version,
            accepted_document.client_ip,
            accepted_document.date_accepted.replace(tzinfo=None),
        ]
        ws.append(data)

    return wb


def _add_worksheet_account_bank_account(account, wb):
    """
    Add Account bank account sheet to workbook data export
    :param account: models.Account object
    :param wb: openpyxl.workbook.Workbook object
    :return: openpyxl.workbook.Workbook object (appended with Account worksheet)
    """
    ws = wb.create_sheet("Bank account")

    # Write header
    header = [
        "Accounr NR",
        "Holder",
        "BIC"
    ]
    ws.append(header)

    for bank_acount in account.bank_accounts.all():
        # Write data
        data = [
            bank_acount.number,
            bank_acount.holder,
            bank_acount.bic,
        ]
        ws.append(data)

    return wb


def _add_worksheet_account_bank_account_mandate(account, wb):
    """
    Add Account bank account mandate sheet to workbook data export
    :param account: models.Account object
    :param wb: openpyxl.workbook.Workbook object
    :return: openpyxl.workbook.Workbook object (appended with Account worksheet)
    """
    ws = wb.create_sheet("Mandates")

    # Write header
    header = [
        "Reference",
        "Content",
        "Sign date"
    ]
    ws.append(header)

    for bank_acount in account.bank_accounts.all():
        for mandate in bank_acount.mandates.all():
            # Write data
            data = [
                mandate.reference,
                mandate.content,
                mandate.signature_date
            ]
            ws.append(data)

    return wb
