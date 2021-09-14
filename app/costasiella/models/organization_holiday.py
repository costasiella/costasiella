import uuid

from django.db import models

from .helpers import model_string


class OrganizationHoliday(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    date_start = models.DateField()
    date_end = models.DateField()
    classes = models.BooleanField(default=False)

    def __str__(self):
        return model_string(self)
