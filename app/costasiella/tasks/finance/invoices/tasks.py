from celery import shared_task

from django.utils.translation import gettext as _
from django.utils import timezone

from ....models import FinanceInvoice


@shared_task
def finance_invoices_mark_overdue():
    """
    Update the status of all sent invoices with due date < today as overdue
    :return: None
    """
    today = timezone.now().date()

    result = FinanceInvoice.objects.filter(status="SENT", date_due__lt=today).update(status="OVERDUE")

    return _("Marked %s invoices as overdue") % result

