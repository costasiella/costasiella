from django.db import models


from .account import Account
from .organization_classpass import OrganizationClasspass
from .finance_payment_method import FinancePaymentMethod

class AccountClasspass(models.Model):
    # add additional fields in here
    # teacher and employee will use OneToOne fields. An account can optionally be a teacher or employee.
    # Editable parameter docs
    # https://docs.djangoproject.com/en/2.2/ref/models/fields/#editable

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    organization_classpass = models.ForeignKey(OrganizationClasspass, on_delete=models.CASCADE)
    date_start = models.DateField()
    date_end = models.DateField(null=True)
    note = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.organization_classpass.name + ' [' + unicode(date_start) + ']'
