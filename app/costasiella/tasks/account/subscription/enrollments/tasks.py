import datetime

from celery import shared_task
from django.utils.translation import gettext as _


@shared_task
def cancel_booked_classes_after_enrollment_end(schedule_item_enrollment_id):
    """
    Add subscription credits for a given month
    :param schedule_item_enrollment
    :return:
    """
    from .....models import ScheduleItemEnrollment

    schedule_item_enrollment = ScheduleItemEnrollment.objects.get(id=schedule_item_enrollment_id)

    account_subscription = schedule_item_enrollment.account_subscription
    account_subscription.cancel_booked_classes_after_enrollment_end(schedule_item_enrollment)

    return _("OK")
