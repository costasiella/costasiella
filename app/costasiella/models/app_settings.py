from django.utils.translation import gettext as _
from django.db import models

from ..modules.encrypted_fields import EncryptedTextField


class AppSettings(models.Model):
    # add additional fields in here

    DATE_FORMATS = (
        ("YYYY-MM-DD", _("YYYY-MM-DD")),
        ("MM-DD-YYYY", _("MM-DD-YYYY")),
        ("DD-MM-YYYY", _("DD-MM-YYYY")),
    )

    TIME_FORMATS = (
        ("24", _("24 Hr (HH:mm)")),
        ("12", _("12 Hr (hh:mm am/pm)")),
    )

    date_format = models.CharField(max_length=255, default="YYYY-MM-DD", choices=DATE_FORMATS)
    time_format = models.CharField(max_length=255, default="24", choices=TIME_FORMATS)

    def __str__(self):
        return "App setting object"
