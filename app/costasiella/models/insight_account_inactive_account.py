from django.db import models

from .account import Account
from .insight_account_inactive import InsightAccountInactive

from .helpers import model_string


class InsightAccountInactiveAccount(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="inactive_reports")
    insight_account_inactive = models.ForeignKey(InsightAccountInactive,
                                                 on_delete=models.CASCADE,
                                                 related_name="accounts")
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return model_string(self)
