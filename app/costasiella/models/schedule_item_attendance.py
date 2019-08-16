from django.utils.translation import gettext as _

from django.db import models


from .schedule_item import ScheduleItem
from .account import Account
from .account_classpass import AccountClasspass
from .account_subscription import AccountSubscription
from .finance_invoice_item import FinanceInvoiceItem

# Create your models here.

class ScheduleItemAttendance(models.Model):
    ATTENDANCE_TYPES = [
        ['TRIAL', _("Trial")],
        ['DROPIN', _("Drop in")],
        ['CLASSPASS', _("Classpass")],
        ['SUBSCRIPTION', _("Subscription")],
        ['COMPLEMENTARY', _("Complementary")],
        ['REVIEW', _("To be reviewed")],
        ['RECONCILE_LATER', _("Reconcile later")],
    ]

    BOOKING_STATUSES = [
        ['BOOKED', _("Booked")],
        ['ATTENDING', _("Attending")],
        ['CANCELLED', _("Cancelled")],
    ]

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    schedule_item = models.ForeignKey(ScheduleItem, on_delete=models.CASCADE)
    account_classpass = models.ForeignKey(AccountClasspass, on_delete=models.CASCADE, null=True)
    account_subscription = models.ForeignKey(AccountSubscription, on_delete=models.CASCADE, null=True)
    finance_invoice_item = models.ForeignKey(FinanceInvoiceItem, on_delete=models.SET_NULL, null=True)
    account_has_membership = models.BooleanField(default=False) # Set to True when account has membership at time of check-in
    attendance_type = models.CharField(max_length=255, choices=ATTENDANCE_TYPES)
    date = models.DateField()
    online_booking = models.BooleanField(default=False)
    booking_status = models.CharField(max_length=255, choices=BOOKING_STATUSES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.schedule_item.id) + ' [' + self.account.full_name + " - " + str(date) + '] ' + attendance_type
    
