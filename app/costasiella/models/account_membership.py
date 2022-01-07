from django.db import models

from .account import Account
from .organization_membership import OrganizationMembership
from .finance_payment_method import FinancePaymentMethod

from .helpers import model_string


class AccountMembership(models.Model):
    # add additional fields in here
    # instructor and employee will use OneToOne fields. An account can optionally be a instructor or employee.
    # Editable parameter docs
    # https://docs.djangoproject.com/en/2.2/ref/models/fields/#editable

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="memberships")
    organization_membership = models.ForeignKey(OrganizationMembership, on_delete=models.CASCADE)
    finance_payment_method = models.ForeignKey(FinancePaymentMethod, on_delete=models.CASCADE, null=True)
    date_start = models.DateField()
    date_end = models.DateField(null=True)
    note = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return model_string(self)

    def set_date_end(self):
        """
           Calculate and set enddate when adding a membership
           return: datetime.date
        """
        def add_months(sourcedate, months):
            month = sourcedate.month - 1 + months
            year = int(sourcedate.year + month / 12)
            month = month % 12 + 1
            last_day_new = calendar.monthrange(year, month)[1]
            day = min(sourcedate.day, last_day_new)

            ret_val = datetime.date(year, month, day)

            last_day_source = calendar.monthrange(sourcedate.year,
                                                  sourcedate.month)[1]

            if sourcedate.day == last_day_source and last_day_source > last_day_new:
                return ret_val
            else:
                delta = datetime.timedelta(days=1)
                return ret_val - delta

        import datetime
        import calendar
        
        if self.organization_membership.validity_unit == 'MONTHS':
            # check for and add months
            months = self.organization_membership.validity
            if months:
                date_end = add_months(self.date_start, months)
        else:
            if self.organization_membership.validity_unit == 'WEEKS':
                days = self.organization_membership.validity * 7
            else:
                days = self.organization_membership.validity

            delta_days = datetime.timedelta(days=days)
            date_end = (self.date_start + delta_days) - datetime.timedelta(days=1)

        self.date_end = date_end

        return date_end