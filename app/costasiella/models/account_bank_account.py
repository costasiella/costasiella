from django.db import models

from .account import Account

from .helpers import model_string
from ..modules.encrypted_fields import EncryptedTextField


class AccountBankAccount(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="bank_accounts")
    number = EncryptedTextField(default="")
    holder = EncryptedTextField(default="")
    bic = EncryptedTextField(default="")
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return model_string(self)
