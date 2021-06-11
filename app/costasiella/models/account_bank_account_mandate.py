from django.db import models

from .account_bank_account import AccountBankAccount

from .helpers import model_string
from ..modules.encrypted_fields import EncryptedTextField


class AccountBankAccountMandate(models.Model):
    account_bank_account = models.ForeignKey(AccountBankAccount, on_delete=models.CASCADE, related_name="mandates")
    reference = EncryptedTextField(default="")
    content = EncryptedTextField(default="")  # Text in OpenStudio
    signature_date = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return model_string(self)
