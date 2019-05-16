from django.contrib.auth.models import AbstractUser
from django.db import models

from ..modules.encrypted_fields import EncryptedTextField

class Account(AbstractUser):
    # add additional fields in here
    # teacher and employee will use OneToOne fields. An account can optionally be a teacher or employee.

    address = EncryptedTextField(max_length=255, default="")

    def __str__(self):
        return self.email