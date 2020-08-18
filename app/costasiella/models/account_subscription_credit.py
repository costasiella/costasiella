from django.utils.translation import gettext as _
from django.utils import timezone

from django.db import models

from .account_subscription import AccountSubscription
from .schedule_item_attendance import ScheduleItemAttendance


class AccountSubscriptionCredit(models.Model):
    # add additional fields in here
    # teacher and employee will use OneToOne fields. An account can optionally be a teacher or employee.
    # Editable parameter docs
    # https://docs.djangoproject.com/en/2.2/ref/models/fields/#editable

    MUTATION_TYPES = [
        ('ADD', _("Add")),
        ('SUB', _("Subtract")),
    ]

    account_subscription = models.ForeignKey(AccountSubscription,
                                             on_delete=models.CASCADE,
                                             related_name="credits")
    schedule_item_attendance = models.ForeignKey(ScheduleItemAttendance,
                                                 on_delete=models.CASCADE,
                                                 null=True)
    mutation_type = models.CharField(max_length=255, choices=MUTATION_TYPES, default="ADD")
    mutation_amount = models.DecimalField(max_digits=20, decimal_places=1)
    description = models.TextField(default="")
    subscription_year = models.IntegerField(null=True)
    subscription_month = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)  # can be used at mutation_datetime
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return str(self.created_at) + ' [' + self.mutation_type + '] ' + str(self.mutation_amount)
