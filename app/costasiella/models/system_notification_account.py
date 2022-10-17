from django.utils.translation import gettext as _
from django.db import models

from .account import Account
from .system_notification import SystemNotification
from ..modules.encrypted_fields import EncryptedTextField

from .helpers import model_string


class SystemNotificationAccount(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="notifications")
    system_notification = models.ForeignKey(SystemNotification, related_name="system_notification_accounts",
                                            on_delete=models.CASCADE)

    def __str__(self):
        return model_string(self)
