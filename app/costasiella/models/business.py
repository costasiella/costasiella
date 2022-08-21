from django.db import models

from .helpers import model_string


class Business(models.Model):
    archived = models.BooleanField(default=False)
    b2b = models.BooleanField(default=False)
    supplier = models.BooleanField(default=False)
    vip = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, default="")
    postcode = models.CharField(max_length=255, default="")
    city = models.CharField(max_length=255, default="")
    country = models.CharField(max_length=255, default="")
    phone = models.CharField(max_length=255, default="")
    phone_2 = models.CharField(max_length=255, default="")
    email_contact = models.EmailField(default="")
    email_billing = models.EmailField(default="")
    registration = models.CharField(max_length=255, default="")
    tax_registration = models.CharField(max_length=255, default="")
    mollie_customer_id = models.CharField(max_length=255, default="", editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return model_string(self)
