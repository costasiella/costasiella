from django.contrib.auth.models import AbstractUser
from django.db import models


from .account import Account
from .organization_subscription import OrganizationSubscription
from .finance_payment_method import FinancePaymentMethod

class AccountSubscription(AbstractUser):
    # add additional fields in here
    # teacher and employee will use OneToOne fields. An account can optionally be a teacher or employee.
    # Editable parameter docs
    # https://docs.djangoproject.com/en/2.2/ref/models/fields/#editable

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    organization_subscription = models.ForeignKey(OrganizationSubscription, on_delete=models.CASCADE)
    date_start = models.DateField()
    date_end = models.DateField(null=True)
    finance_payment_method = models.ForeignKey(FinancePaymentMethod, on_delete=models.CASCADE)
    note = models.TextField(default="")
    registration_fee_paid = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.organization_subscription.name
