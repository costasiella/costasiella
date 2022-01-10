from django.utils.translation import gettext as _
from django.db import models

from .account import Account

from .helpers import model_string
from ..modules.encrypted_fields import EncryptedTextField
from .choices.account_note_types import get_account_note_types


class AccountNote(models.Model):
    class Meta:
        permissions = [
            ('view_accountnoteinstructors', _("Can view instructor notes")),
            ('view_accountnotebackoffice', _("Can view backoffice notes")),
        ]

    NOTE_TYPES = get_account_note_types()

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="notes")
    note_by = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="notes_made")
    note_type = models.CharField(max_length=255, choices=NOTE_TYPES)
    note = EncryptedTextField(default="")
    injury = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return model_string(self)
