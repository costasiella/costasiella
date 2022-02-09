import uuid

from django.db import models

from .helpers import model_string

from .organization_location import OrganizationLocation


class OrganizationHoliday(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    date_start = models.DateField()
    date_end = models.DateField()
    classes = models.BooleanField(default=True)
    organization_locations = models.ManyToManyField(
        OrganizationLocation,
        through='OrganizationHolidayLocation',
        related_name='holidays'
    )

    def __str__(self):
        return model_string(self)
