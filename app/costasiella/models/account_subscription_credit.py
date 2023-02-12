from django.utils.translation import gettext as _
from django.utils import timezone

from django.db import models

from .account_subscription import AccountSubscription
from .schedule_item_attendance import ScheduleItemAttendance

from .helpers import model_string


class AccountSubscriptionCredit(models.Model):
    # add additional fields in here
    # instructor and employee will use OneToOne fields. An account can optionally be a instructor or employee.
    # Editable parameter docs
    # https://docs.djangoproject.com/en/2.2/ref/models/fields/#editable

    MUTATION_TYPES = [
        ("SINGLE", _("Single")),
        ('ADD', _("Add")),
        ('SUB', _("Subtract")),
    ]

    advance = models.BooleanField(default=False)
    reconciled = models.DateTimeField(null=True)
    account_subscription = models.ForeignKey(AccountSubscription,
                                             on_delete=models.CASCADE,
                                             related_name="credits")
    schedule_item_attendance = models.ForeignKey(ScheduleItemAttendance,
                                                 on_delete=models.SET_NULL,
                                                 null=True)
    expiration = models.DateField()
    description = models.TextField(default="")
    subscription_year = models.IntegerField(null=True)
    subscription_month = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)  # can be used at mutation_datetime
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    # Legacy fields begin - Can be removed from mid 2023.
    # On removal, include backwards compatibility break in release notes.
    mutation_type = models.CharField(max_length=255, choices=MUTATION_TYPES, default="SINGLE")
    mutation_amount = models.DecimalField(max_digits=20, decimal_places=1, default=1)
    # Legacy fields end

    def __str__(self):
        return model_string(self)
