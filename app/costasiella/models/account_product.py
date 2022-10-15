from decimal import Decimal

from django.db import models
from django.db.models import Q
from django.utils import timezone

from .account import Account
from .organization_product import OrganizationProduct

from .helpers import model_string


class AccountProduct(models.Model):
    # add additional fields in here
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="products")
    organization_product = models.ForeignKey(OrganizationProduct, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal(1))
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return model_string(self)
        