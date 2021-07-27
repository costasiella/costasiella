from django.utils.translation import gettext as _

from django.db import models

from .helpers import model_string
from ..modules.encrypted_fields import EncryptedTextField


class OrganizationAnnouncement(models.Model):
    display_public = models.BooleanField(default=False)  # Published
    display_shop = models.BooleanField(default=False)
    display_backend = models.BooleanField(default=False)
    title = EncryptedTextField(default="")
    content = EncryptedTextField(default="")
    date_start = models.DateField()
    date_end = models.DateField()
    priority = models.IntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return model_string(self)
