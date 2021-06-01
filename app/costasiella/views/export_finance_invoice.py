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

# Django-graphql-jwt imports begin
from calendar import timegm
from datetime import datetime

import django
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

import jwt

from .jwt_settings import jwt_settings
# Django-graphql-jwt imports end


def _verifiy_permission_or_account(request, finance_invoice, **kwargs):
    """

    :param request:
    :param finance_invoice:
    :return:
    """
    # user = request.user # This should work, but doesn't at 05-02-2012 for some reason. Check again later
    # Fetch token using some code from djan-graphql-jwt
    user = None
    token = get_credentials(request, **kwargs)
    if token is not None:
        user = get_user_by_token(token, request)

    if not user:
        return False

    if user.has_perm('costasiella.view_financeinvoice') or finance_invoice.account == user:
        return True
    else:
        return False


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
    logo_url = organization.logo_invoice.url if organization.logo_invoice else ""
    items = FinanceInvoiceItem.objects.filter(
        finance_invoice=finance_invoice
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
            "logo_url": logo_url,
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

    return [finance_invoice, rendered_template]


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
def invoice_pdf(request, node_id, **kwargs):
    """
    Export invoice as PDF

    :param: POST: node_id - FinanceInvoiceNode ID
    """
    import weasyprint
    print("InvoiceID:")
    print(node_id)

    finance_invoice, html = invoice_html(node_id)
    if not _verifiy_permission_or_account(request, finance_invoice):
        raise Http404(_("Invoice not found..."))

    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()
    pdf = weasyprint.HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(buffer)

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)

    filename = _('invoice') + '_' + finance_invoice.invoice_number + '.pdf'

    return FileResponse(buffer, as_attachment=True, filename=filename)


def invoice_pdf_preview(request, node_id):
    """
    Preview for invoice_pdf

    :param: POST: node_id - FinanceInvoiceNode ID
    """
    print("InvoiceID:")
    print(node_id)
    # print(request.POST.node_id)

    finance_invoice, html = invoice_html(node_id)
    if not _verifiy_permission_or_account(request, finance_invoice):
        raise Http404(_("Invoice not found..."))

    return HttpResponse(html)


### Below is a lot of code from django-graphql-jwt.
"""
We probably don't need it, but for some reason the middleware doesn't seem to pass users properly with the current 
versions. So it can be here for now, until it's fixed upstream.
Everything below here can be deleted again once request.user works again. 
"""



def jwt_payload(user, context=None):
    username = user.get_username()

    if hasattr(username, 'pk'):
        username = username.pk

    payload = {
        user.USERNAME_FIELD: username,
        'exp': datetime.utcnow() + jwt_settings.JWT_EXPIRATION_DELTA,
    }

    if jwt_settings.JWT_ALLOW_REFRESH:
        payload['origIat'] = timegm(datetime.utcnow().utctimetuple())

    if jwt_settings.JWT_AUDIENCE is not None:
        payload['aud'] = jwt_settings.JWT_AUDIENCE

    if jwt_settings.JWT_ISSUER is not None:
        payload['iss'] = jwt_settings.JWT_ISSUER

    return payload


def jwt_encode(payload, context=None):
    return jwt.encode(
        payload,
        jwt_settings.JWT_PRIVATE_KEY or jwt_settings.JWT_SECRET_KEY,
        jwt_settings.JWT_ALGORITHM,
    ).decode('utf-8')


def jwt_decode(token, context=None):
    return jwt.decode(
        token,
        jwt_settings.JWT_PUBLIC_KEY or jwt_settings.JWT_SECRET_KEY,
        jwt_settings.JWT_VERIFY,
        options={
            'verify_exp': jwt_settings.JWT_VERIFY_EXPIRATION,
        },
        leeway=jwt_settings.JWT_LEEWAY,
        audience=jwt_settings.JWT_AUDIENCE,
        issuer=jwt_settings.JWT_ISSUER,
        algorithms=[jwt_settings.JWT_ALGORITHM],
    )


def get_http_authorization(request):
    auth = request.META.get(jwt_settings.JWT_AUTH_HEADER_NAME, '').split()
    prefix = jwt_settings.JWT_AUTH_HEADER_PREFIX

    if len(auth) != 2 or auth[0].lower() != prefix.lower():
        return request.COOKIES.get(jwt_settings.JWT_COOKIE_NAME)
    return auth[1]


def get_token_argument(request, **kwargs):
    if jwt_settings.JWT_ALLOW_ARGUMENT:
        input_fields = kwargs.get('input')

        if isinstance(input_fields, dict):
            kwargs = input_fields

        return kwargs.get(jwt_settings.JWT_ARGUMENT_NAME)
    return None


def get_credentials(request, **kwargs):
    return (get_token_argument(request, **kwargs) or
            get_http_authorization(request))


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


def get_user_by_natural_key(username):
    UserModel = get_user_model()
    try:
        return UserModel._default_manager.get_by_natural_key(username)
    except UserModel.DoesNotExist:
        return None


def get_user_by_payload(payload):
    username = jwt_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER(payload)

    if not username:
        raise exceptions.JSONWebTokenError(_('Invalid payload'))

    user = jwt_settings.JWT_GET_USER_BY_NATURAL_KEY_HANDLER(username)

    if user is not None and not getattr(user, 'is_active', True):
        raise exceptions.JSONWebTokenError(_('User is disabled'))
    return user


def refresh_has_expired(orig_iat, context=None):
    exp = orig_iat + jwt_settings.JWT_REFRESH_EXPIRATION_DELTA.total_seconds()
    return timegm(datetime.utcnow().utctimetuple()) > exp


def set_cookie(response, key, value, expires):
    kwargs = {
        'expires': expires,
        'httponly': True,
        'secure': jwt_settings.JWT_COOKIE_SECURE,
        'path': jwt_settings.JWT_COOKIE_PATH,
        'domain': jwt_settings.JWT_COOKIE_DOMAIN,
    }
    if django.VERSION >= (2, 1):
        kwargs['samesite'] = jwt_settings.JWT_COOKIE_SAMESITE

    response.set_cookie(key, value, **kwargs)


def delete_cookie(response, key):
    response.delete_cookie(
        key,
        path=jwt_settings.JWT_COOKIE_PATH,
        domain=jwt_settings.JWT_COOKIE_DOMAIN,
    )

def get_user_by_token(token, context=None):
    payload = get_payload(token, context)
    return get_user_by_payload(payload)