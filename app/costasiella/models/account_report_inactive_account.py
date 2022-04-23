from django.db import models

from .account import Account
from .account_report_inactive import AccountReportInactive

from .helpers import model_string


class AccountReportInactiveAccount(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="inactive_reports")
    account_report_inactive = models.ForeignKey(AccountReportInactive,
                                                on_delete=models.CASCADE,
                                                related_name="accounts")
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return model_string(self)
