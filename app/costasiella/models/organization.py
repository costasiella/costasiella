from django.utils.translation import gettext as _
from django.db.models import Q

from django.db import models


class Organization(models.Model):
    archived = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    address = models.TextField(default="")
    phone = models.CharField(max_length=255, default="")
    email = models.EmailField(default="")
    registration = models.CharField(max_length=255, default="")
    tax_registration = models.CharField(max_length=255, default="")


    def __str__(self):
        return self.name
    
