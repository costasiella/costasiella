from django.utils.translation import gettext as _
from django.db.models import Q

from django.db import models

from .finance_costcenter import FinanceCostCenter
from .finance_glaccount import FinanceGLAccount
from .finance_taxrate import FinanceTaxRate
from .organization_membership import OrganizationMembership

from ..modules.finance_tools import display_float_as_amount


class OrganizationSubscription(models.Model):
    SUBSCRIPTION_UNITS = (
        ("WEEK", _("Week")),
        ("MONTH", _("Month"))
    )

    archived = models.BooleanField(default=False)
    display_public = models.BooleanField(default=True)
    display_shop = models.BooleanField(default=True)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    sort_order = models.PositiveIntegerField(default=0)
    min_duration = models.PositiveIntegerField()
    classes = models.PositiveIntegerField()
    subscription_unit = models.CharField(max_length=10, choices=SUBSCRIPTION_UNITS, default="DAYS")
    reconciliation_classes = models.PositiveSmallIntegerField(default=0)
    credit_validity = models.PositiveIntegerField(default=1)
    unlimited = models.BooleanField(default=False)
    terms_and_conditions = models.TextField()
    registration_fee = models.DecimalField(max_digits=20, decimal_places=2)
    organization_membership = models.ForeignKey(OrganizationMembership, on_delete=models.CASCADE, null=True)
    quick_stats_amount = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    finance_glaccount = models.ForeignKey(FinanceGLAccount, on_delete=models.CASCADE, null=True)
    finance_costcenter = models.ForeignKey(FinanceCostCenter, on_delete=models.CASCADE, null=True)


    def get_price_on_date(self, date, display=False):
        query_set = self.organizationsubscriptionprice_set.filter(
            Q(date_start__lte = date) & 
            (Q(date_end__gte = date) | Q(date_end__isnull = True))
        )
        
        if query_set.exists():
            price = query_set.first().price
            if display:
                return display_float_as_amount(price)
            else:
                return price
        else:
            return None


    def __str__(self):
        return self.name
    
