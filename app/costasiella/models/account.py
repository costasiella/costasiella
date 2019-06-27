from django.contrib.auth.models import AbstractUser
from django.db import models

from ..modules.encrypted_fields import EncryptedTextField

class Account(AbstractUser):
    # add additional fields in here
    # teacher and employee will use OneToOne fields. An account can optionally be a teacher or employee.
    # Editable parameter docs
    # https://docs.djangoproject.com/en/2.2/ref/models/fields/#editable

    full_name = models.CharField(max_length=255, default="", editable=False)
    search_name = models.CharField(max_length=255, default="", editable=False)
    gender = EncryptedTextField(default="")
    date_of_birth = EncryptedTextField(data_type="date", default="")
    address = EncryptedTextField(default="")
    postcode = EncryptedTextField(default="")
    city = EncryptedTextField(default="")
    country = EncryptedTextField(default="")
    phone = EncryptedTextField(default="")
    mobile = EncryptedTextField(default="")
    emergency = EncryptedTextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        name = [self.first_name, self.last_name]
        self.full_name = " ".join(name)
        self.search_name = self.full_name.lower()
        super(Account, self).save(*args, **kwargs)