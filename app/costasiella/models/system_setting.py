from django.utils.translation import gettext as _
from django.db import models

from ..modules.encrypted_fields import EncryptedTextField


class SystemSetting(models.Model):
    setting = models.CharField(max_length=255)
    value = EncryptedTextField(default="")

    def __str__(self):
        return "%s [%s]" % (self.setting, self.value)
