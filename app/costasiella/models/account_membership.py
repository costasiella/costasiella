from django.db import models


from .account import Account
from .organization_membership import OrganizationMembership
from .finance_payment_method import FinancePaymentMethod

class AccountMembership(models.Model):
    # add additional fields in here
    # teacher and employee will use OneToOne fields. An account can optionally be a teacher or employee.
    # Editable parameter docs
    # https://docs.djangoproject.com/en/2.2/ref/models/fields/#editable

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    organization_membership = models.ForeignKey(OrganizationMembership, on_delete=models.CASCADE)
    finance_payment_method = models.ForeignKey(FinancePaymentMethod, on_delete=models.CASCADE, null=True)
    date_start = models.DateField()
    date_end = models.DateField(null=True)
    note = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.organization_membership.name + ' [' + unicode(date_start) + ']'
