from django.db import models

from .account import Account

from .helpers import model_string
from ..modules.encrypted_fields import EncryptedTextField


class AccountNote(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="notes")
    note_by = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="notes_made")
    backoffice_note = models.BooleanField(default=False)
    teacher_note = models.BooleanField(default=False)
    note = EncryptedTextField(default="")
    injury = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return model_string(self)
