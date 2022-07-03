import datetime

from django.db import models
from django.utils import timezone

from .helpers import model_string


class InsightAccountInactive(models.Model):
    no_activity_after_date = models.DateField()
    count_inactive_accounts = models.IntegerField(default=0)
    count_deleted_inactive_accounts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return model_string(self)

    def delete_inactive_accounts(self):
        """
        Remove linked inactive accounts
        :return: int - count of deleted accounts
        """
        from .insight_account_inactive_account import InsightAccountInactiveAccount

        count_deleted_accounts = 0

        qs = InsightAccountInactiveAccount.objects.filter(
            insight_account_inactive=self
        )
        for insight_account_inactive_account in qs:
            insight_account_inactive_account.account.delete()
            count_deleted_accounts += 1

        self.count_deleted_inactive_accounts = count_deleted_accounts
        self.save()

        return count_deleted_accounts
