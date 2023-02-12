import logging

from django.utils.translation import gettext as _
from django.utils import timezone

from django.db import models

from .account_subscription import AccountSubscription

logger = logging.getLogger(__name__)


class AccountSubscriptionPause(models.Model):
    # add additional fields in here
    account_subscription = models.ForeignKey(AccountSubscription,
                                             on_delete=models.CASCADE,
                                             related_name="pauses")
    date_start = models.DateField()
    date_end = models.DateField()
    description = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return str(self.account_subscription) + ' paused [' + str(self.date_start) + ' - ' + str(self.date_end) + ' ]'

    def cancel_booked_classes_during_pause(self):
        """
        Cancel classes booked using subscription during pause
        """
        from .account_subscription_credit import AccountSubscriptionCredit
        from .schedule_item_attendance import ScheduleItemAttendance

        # Fetch booked classes
        qs = ScheduleItemAttendance.objects.filter(
            account_subscription=self.account_subscription,
            date__gte=self.date_start,
            date__lte=self.date_end,
        )
        # Cancel class bookings
        qs.update(booking_status='CANCELLED')

        # Refund credits
        for schedule_item_attendance in qs:
            account_subscription_credit = AccountSubscriptionCredit.objects.filter(
                schedule_item_attendance=schedule_item_attendance,
            ).first()
            account_subscription_credit.schedule_item_attendance = None
            account_subscription_credit.save()

        logger.info(f"Subscription {self.account_subscription.id} paused: cancelled classes booked during pause from \
            {self.date_start} - {self.date_end}")
