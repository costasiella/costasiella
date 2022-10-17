from django.utils.translation import gettext as _
from django.db import models

from .account import Account
from .system_mail_template import SystemMailTemplate
from ..modules.encrypted_fields import EncryptedTextField


class SystemNotification(models.Model):
    name = models.CharField(max_length=255, editable=False)
    system_mail_template = models.ForeignKey(SystemMailTemplate, related_name="notifications", on_delete=models.CASCADE)
    accounts = models.ManyToManyField(
        Account,
        through='SystemNotificationAccount',
        related_name='accounts'
    )

    def __str__(self):
        return "System notification: %s" % self.name
