from django.db import models
from django.utils import timezone
import uuid

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

    def has_direct_debit_mandate(self):
        from .account_bank_account_mandate import AccountBankAccountMandate

        return AccountBankAccountMandate.objects.filter(account_bank_account=self).exists()

    def add_mandate(self):
        from .account_bank_account_mandate import AccountBankAccountMandate

        account_bank_account_mandate = AccountBankAccountMandate(
            account_bank_account=self,
            signature_date=timezone.now().date(),  # Today
            reference=str(uuid.uuid4())
        )
        account_bank_account_mandate.save()
