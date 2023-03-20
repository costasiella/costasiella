import datetime
import logging

from celery import shared_task
from django.utils.translation import gettext as _


logger = logging.getLogger(__name__)


@shared_task
def cancel_booked_classes_after_enrollment_end(account_subscription_id, schedule_item_id, cancel_bookings_from_date):
    """
    Cancel classes booked on enrollment after given date
    :param account_subscription_id
    :return:
    """
    from .....models import AccountSubscription, ScheduleItem

    logger.info(f"Cancelling classes booked on subscription {account_subscription_id} \
        for class {schedule_item_id}: Enrollment ended")


    schedule_item = ScheduleItem.objects.get(pk=schedule_item_id)
    account_subscription = AccountSubscription.objects.get(pk=account_subscription_id)
    account_subscription.cancel_booked_classes_after_enrollment_end(
        schedule_item=schedule_item,
        cancel_bookings_from_date=cancel_bookings_from_date
    )

    return _("OK")
