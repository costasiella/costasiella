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

    def __str__(self):
        return self.name
