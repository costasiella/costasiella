from django.db import models

from ..modules.encrypted_fields import EncryptedTextField


class Business(models.Model):
    archived = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    address = EncryptedTextField(default="")
    postcode = EncryptedTextField(default="")
    city = EncryptedTextField(default="")
    country = EncryptedTextField(default="")
    phone = EncryptedTextField(default="")
    mobile = EncryptedTextField(default="")
    email = models.EmailField(default="")
    registration = models.CharField(max_length=255, default="")
    tax_registration = models.CharField(max_length=255, default="")
    mollie_customer_id = models.CharField(max_length=255, default="", editable=False)

    def __str__(self):
        return self.name
