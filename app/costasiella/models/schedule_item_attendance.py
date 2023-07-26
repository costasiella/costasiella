from django.utils.translation import gettext as _

import datetime
import pytz

from django.db import models

from .schedule_item import ScheduleItem
from .account import Account
from .account_classpass import AccountClasspass
from .account_subscription import AccountSubscription
from .account_schedule_event_ticket import AccountScheduleEventTicket
from .finance_invoice_item import FinanceInvoiceItem

from .choices.schedule_item_attendance_types import get_schedule_item_attendance_types

# Create your models here.


class ScheduleItemAttendance(models.Model):
    ATTENDANCE_TYPES = get_schedule_item_attendance_types()

    BOOKING_STATUSES = [
        ['BOOKED', _("Booked")],
        ['ATTENDING', _("Attending")],
        ['CANCELLED', _("Cancelled")],
    ]

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    schedule_item = models.ForeignKey(ScheduleItem, on_delete=models.CASCADE,
                                      related_name="attendances")
    account_classpass = models.ForeignKey(AccountClasspass, on_delete=models.CASCADE, null=True,
                                          related_name="classes")
    account_subscription = models.ForeignKey(AccountSubscription, on_delete=models.CASCADE, null=True)
    account_schedule_event_ticket = models.ForeignKey(AccountScheduleEventTicket, on_delete=models.CASCADE, null=True)
    finance_invoice_item = models.ForeignKey(FinanceInvoiceItem, on_delete=models.SET_NULL, null=True)
    attendance_type = models.CharField(max_length=255, choices=ATTENDANCE_TYPES)
    date = models.DateField()
    online_booking = models.BooleanField(default=False)
    booking_status = models.CharField(max_length=255, choices=BOOKING_STATUSES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        from django.forms.models import model_to_dict
        data = model_to_dict(self)
        values = ["-----", str(type(self)), "-----"]
        for key, value in data.items():
            values.append(f'{key}: {value}')

        values.append("-----")
        return "\n".join(values)

        # return str(self.schedule_item.id) + ' [' + self.account.full_name + " - " + str(self.date) + '] ' + \
        #        self.attendance_type

    def get_cancel_before(self):
        """
        Return "cancel before" datetime; Datetime after which this booking can no longer be cancelled
        :return:
        """
        from ..dudes import SystemSettingDude

        system_setting_dude = SystemSettingDude()
        workflow_class_cancel_until = system_setting_dude.get("workflow_class_cancel_until")
        if not workflow_class_cancel_until:
            # Set a default value of 0 hours in advance to allow class cancellation; always allow
            workflow_class_cancel_until = 0

        # Fetch local start time
        dt_start = datetime.datetime(self.date.year,
                                     self.date.month,
                                     self.date.day,
                                     self.schedule_item.time_start.hour,
                                     self.schedule_item.time_start.minute)
        # Times in the DB are already local time, don't add or subtract anything
        dt_start = pytz.utc.localize(dt_start).astimezone(pytz.timezone("Etc/UTC"))
        # Check until when this class can be cancelled
        delta = datetime.timedelta(hours=int(workflow_class_cancel_until))

        return dt_start - delta

    def cancel(self):
        self.booking_status = "CANCELLED"
        self.save()

        self._on_cancel()


    def _on_cancel(self):
        self._on_cancel_refund_subscription_credit()
        self._on_cancel_refund_classpass_class()


    def _on_cancel_refund_subscription_credit(self):
        from .account_subscription_credit import AccountSubscriptionCredit

        if self.account_subscription:
            account_subscription_credit = AccountSubscriptionCredit.objects.filter(
                schedule_item_attendance=self,
            ).first()

            if account_subscription_credit:
                account_subscription_credit.schedule_item_attendance = None
                account_subscription_credit.save()

    def _on_cancel_refund_classpass_class(self):
        if self.account_classpass:
             self.account_classpass.update_classes_remaining()
