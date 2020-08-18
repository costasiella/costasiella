from django.utils.translation import gettext as _
from django.utils import timezone

from django.db import models

from .account_subscription import AccountSubscription


class AccountSubscriptionBlock(models.Model):
    # add additional fields in here
    account_subscription = models.ForeignKey(AccountSubscription,
                                             on_delete=models.CASCADE,
                                             related_name="blocks")
    date_start = models.DateField()
    date_end = models.DateField()
    description = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return str(self.account_subscription) + ' blocked [' + str(self.date_start) + ' - ' + str(self.date_end) + ' ]'
