import datetime

from celery import shared_task
from django.utils.translation import gettext as _


@shared_task
def cancel_booked_classes_on_enrollment_end(schedule_item_enrollment):
    """
    Add subscription credits for a given month
    :param schedule_item_enrollment
    :return:
    """

    account_subscription = schedule_item_enrollment.account_subscription
    account_subscription.cancel_booked_classes_after_enrollment_end(schedule_item_enrollment)

    return _("OK")
