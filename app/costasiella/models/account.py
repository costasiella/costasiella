from django.contrib.auth.models import AbstractUser
from django.db import models

from ..modules.encrypted_fields import EncryptedCharField

class Account(AbstractUser):
    # add additional fields in here
    # teacher and employee will use OneToOne fields. An account can optionally be a teacher or employee.

    address = EncryptedCharField(max_length=255, default=None)

    def __str__(self):
        return self.email