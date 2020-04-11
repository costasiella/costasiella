from django.utils.translation import gettext as _
from django.db import models

from ..modules.encrypted_fields import EncryptedTextField

class SystemSetting(models.Model):
    # add additional fields in here

    setting = models.CharField(max_length=255)
    value = EncryptedTextField(default="")

    def __str__(self):
        return "system setting object"