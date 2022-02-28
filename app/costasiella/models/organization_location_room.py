from django.db import models
from .organization_location import OrganizationLocation


# Create your models here.
class OrganizationLocationRoom(models.Model):
    organization_location = models.ForeignKey(OrganizationLocation,
                                              on_delete=models.CASCADE,
                                              related_name='rooms')
    archived = models.BooleanField(default=False)
    display_public = models.BooleanField(default=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.organization_location.name + ' ' + 'Room' + ': ' + self.name
