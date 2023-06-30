import csv
import io

from django.utils.translation import gettext as _
from django.http import Http404, StreamingHttpResponse

from ...models import AppSettings, FinancePaymentBatch, FinancePaymentBatchExport
from ...modules.gql_tools import require_login_and_permission, get_rid
from ...modules.graphql_jwt_tools import get_user_from_cookie


def _verifiy_permission(request):
    """

    :param request:
    :param finance_invoice:
    :return:
    """
    user = get_user_from_cookie(request)
    if not user:
        return False

    return user.has_perm('costasiella.view_financepaymentbatch')


def export_csv_finance_payment_batch(request, node_id, **kwargs):
    """
    Export invoice as PDF

    :param: POST: node_id - FinanceInvoiceNode ID
    """
    import weasyprint
    from ...dudes import AppSettingsDude

    app_settings_dude = AppSettingsDude()
    date_format = app_settings_dude.date_format

    rid = get_rid(node_id)
    finance_payment_batch = FinancePaymentBatch.objects.get(id=rid.id)
    if not _verifiy_permission(request):
        raise Http404(_("Finance Payment Batch not found..."))

    # Log export into exports table
    user = get_user_from_cookie(request)
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
        # 'Location'
    ])

    # organization_location = ""
    # if finance_payment_batch.organization_location:
    #     organization_location = finance_payment_batch.organization_location.name
    batch_items = finance_payment_batch.items.all()
    for item in batch_items:

        writer.writerow([
            item.account.id,
            item.account_holder,
            item.account_number,
            item.account_bic,
            item.mandate_signature_date.strftime(date_format),
            item.mandate_reference,
            item.currency,
            item.amount,
            item.description,
            finance_payment_batch.execution_date.strftime(date_format),
            # organization_location
        ])

    buffer.seek(0)
    batch_name = finance_payment_batch.name.replace(' ', '_')
    filename = _('payment_batch') + '_' + batch_name

    response = StreamingHttpResponse(buffer, content_type="text/csv")
    response["Content-Disposition"] = (
            "attachment; filename=%s.csv" % filename
    )

    return response
