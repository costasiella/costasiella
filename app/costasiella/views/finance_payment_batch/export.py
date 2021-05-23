import csv
import io

from django.utils.translation import gettext as _
from django.utils import timezone
from django.shortcuts import redirect, render
from django.http import Http404, StreamingHttpResponse
from django.db.models import Q
from django.template.loader import get_template, render_to_string


# from django.template.loader import render_to_string
# rendered = render_to_string('my_template.html', {'foo': 'bar'})

from ...models import AppSettings, FinancePaymentBatch, FinancePaymentBatchExport
from ...modules.gql_tools import require_login_and_permission, get_rid

# Django-graphql-jwt imports begin
from calendar import timegm
from datetime import datetime

import django
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

import jwt

from ..jwt_settings import jwt_settings
# Django-graphql-jwt imports end


def _get_user(request, **kwargs):
    user = None
    token = get_credentials(request, **kwargs)
    if token is not None:
        user = get_user_by_token(token, request)

    return user


def _verifiy_permission(request, **kwargs):
    """

    :param request:
    :param finance_invoice:
    :return:
    """
    # user = request.user # This should work, but doesn't at 05-02-2012 for some reason. Check again later
    # Fetch token using some code from djan-graphql-jwt
    print(request.user)

    user = _get_user(request)
    if not user:
        return False

    return user.has_perm('costasiella.view_financepaymentbatch')


def export_csv_finance_payment_batch(request, node_id, **kwargs):
    """
    Export invoice as PDF

    :param: POST: node_id - FinanceInvoiceNode ID
    """
    import weasyprint
    print("batchID:")
    print(node_id)

    rid = get_rid(node_id)
    print(rid)
    finance_payment_batch = FinancePaymentBatch.objects.get(id=rid.id)
    if not _verifiy_permission(request):
        raise Http404(_("Finance Payment Batch not found..."))

    # Log export into exports table
    user = _get_user(request)
    finance_payment_batch_export = FinancePaymentBatchExport(
        finance_payment_batch=finance_payment_batch,
        account=user
    )
    finance_payment_batch_export.save()

    # Create a file-like buffer to receive csv data.
    buffer = io.StringIO()
    writer = csv.writer(buffer)

    # write the header
    writer.writerow([
        'accountID',
        'Account holder',
        'Account number',
        'BIC',
        'Mandate Signature Date',
        'Mandate Reference',
        'Currency',
        'Amount',
        'Description',
        'Execution Date',
        'Location'
    ])

    organization_location = ""
    if finance_payment_batch.organization_location:
        organization_location = finance_payment_batch.organization_location.name
    batch_items = finance_payment_batch.items.all()
    for item in batch_items:

        writer.writerow([
            item.account.id,
            item.account_holder,
            item.account_number,
            item.account_bic,
            item.mandate_signature_date,
            item.mandate_reference,
            item.currency,
            item.amount,
            item.description,
            finance_payment_batch.execution_date,
            organization_location
        ])

    buffer.seek(0)
    batch_name = finance_payment_batch.name.replace(' ', '_')
    filename = _('payment_batch') + '_' + batch_name

    response = StreamingHttpResponse(buffer, content_type="text/csv")
    response["Content-Disposition"] = (
            "attachment; filename=%s.csv" % filename
    )

    return response


"""
Below is a lot of code from django-graphql-jwt.
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
