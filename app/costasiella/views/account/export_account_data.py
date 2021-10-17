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

    #TODO Add functions to add sheets to the workbook; 1 per table

    # # Create a file-like buffer to receive XLSX data.
    buffer = io.BytesIO()
    wb.save(buffer)

    ws = wb.create_sheet(title="test")
    ws.append(['hello', 'world'])

    buffer.seek(0)
    account_name = user.full_name.replace(" ", "_")
    filename = _('account_data') + '_' + account_name + ".xlsx"

    return FileResponse(buffer, as_attachment=True, filename=filename)

    # response = StreamingHttpResponse(buffer, content_type="text/")
    # response["Content-Disposition"] = (
    #         "attachment; filename=%s.csv" % filename
    # )

    # return response
