from django.db import models
from sorl.thumbnail import ImageField


class Organization(models.Model):
    archived = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    address = models.TextField(default="")
    phone = models.CharField(max_length=255, default="")
    email = models.EmailField(default="")
    registration = models.CharField(max_length=255, default="")
    tax_registration = models.CharField(max_length=255, default="")
    logo_login = ImageField(upload_to='organization', default=None)
    logo_invoice = ImageField(upload_to='organization', default=None)
    logo_email = ImageField(upload_to='organization', default=None)
    logo_shop_header = ImageField(upload_to='organization', default=None)
    logo_self_checkin = ImageField(upload_to='organization', default=None)
    branding_color_background = models.CharField(max_length=255, default="")
    branding_color_text = models.CharField(max_length=255, default="")
    branding_color_accent = models.CharField(max_length=255, default="")
    branding_color_secondary = models.CharField(max_length=255, default="")

    def __str__(self):
        return self.name
