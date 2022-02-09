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

from .helpers import model_string


# Create your models here
class ScheduleItemEnrollment(models.Model):
    schedule_item = models.ForeignKey(ScheduleItem, related_name="enrollments", on_delete=models.CASCADE)
    account_subscription = models.ForeignKey(AccountSubscription, related_name="enrollments", on_delete=models.CASCADE)
    date_start = models.DateField()
    date_end = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return model_string(self)
