from django.utils.translation import gettext as _
from django.db import models

from ..modules.encrypted_fields import EncryptedTextField


class SystemMailTemplate(models.Model):
    # add additional fields in here

    name = models.CharField(max_length=255, editable=False)
    subject = models.TextField()
    title = models.TextField()
    description = models.TextField(null=True)
    content = models.TextField()
    comments = models.TextField(null=True)

    def __str__(self):
        return "system mail template: %s" % self.name
