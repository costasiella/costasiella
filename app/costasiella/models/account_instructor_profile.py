from django.db import models


from .account import Account
from .helpers import model_string
from ..modules.encrypted_fields import EncryptedTextField


class AccountInstructorProfile(models.Model):
    # add additional fields in here
    # instructor and employee will use OneToOne fields. An account can optionally be a instructor or employee.
    # Editable parameter docs
    # https://docs.djangoproject.com/en/2.2/ref/models/fields/#editable
    account = models.OneToOneField(
        Account,
        on_delete=models.CASCADE,
        primary_key=True
    )
    classes = models.BooleanField(default=True)
    appointments = models.BooleanField(default=False)
    events = models.BooleanField(default=False)
    role = EncryptedTextField(default="")
    education = EncryptedTextField(default="")
    bio = EncryptedTextField(default="")
    url_bio = EncryptedTextField(default="")
    url_website = EncryptedTextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return model_string(self)