from django.utils.translation import gettext as _
from django.utils import timezone

from django.db import models

from .account_subscription import AccountSubscription


class AccountSubscriptionAltPrice(models.Model):
    # add additional fields in here
    account_subscription = models.ForeignKey(AccountSubscription,
                                             on_delete=models.CASCADE,
                                             related_name="alt_prices")
    subscription_year = models.IntegerField(null=True)
    subscription_month = models.IntegerField(null=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    description = models.TextField(default="")
    note = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return str(self.account_subscription) + ' alt_price [' + str(self.subscription_year) + ' - ' + \
               str(self.subscription_month) + ' ] ' + str(self.amount)
