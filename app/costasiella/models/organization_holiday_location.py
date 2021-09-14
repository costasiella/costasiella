import uuid

from django.db import models

from .helpers import model_string

from .organization_holiday import OrganizationHoliday
from .organization_location import OrganizationLocation


class OrganizationHolidayLocation(models.Model):
    organization_holiday = models.ForeignKey(OrganizationHoliday, on_delete=models.CASCADE)
    organization_location = models.ForeignKey(OrganizationLocation, on_delete=models.CASCADE)

    def __str__(self):
        return model_string(self)
