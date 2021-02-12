from django.utils.translation import gettext as _

from django.db import models

from .finance_tax_rate import FinanceTaxRate
from .organization_subscription import OrganizationSubscription


class OrganizationSubscriptionPrice(models.Model):
    organization_subscription = models.ForeignKey(OrganizationSubscription, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    finance_tax_rate = models.ForeignKey(FinanceTaxRate, on_delete=models.SET_NULL, null=True)
    date_start = models.DateField()
    date_end = models.DateField(null=True)

    class Meta:
        ordering = ['-date_start']
    
    def __str__(self):
        return self.organization_subscription.name + ' ' + self.date_start + ' - ' + self.price
