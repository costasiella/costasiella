from django.db import models

from .account import Account

from .helpers import model_string


class AccountBankAccount(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="bank_accounts")
    number = models.CharField(max_length=255)
    holder = models.CharField(max_length=255)
    bic = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return model_string(self)
