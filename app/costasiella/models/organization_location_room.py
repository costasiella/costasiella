import uuid

from django.db import models
from .organization_location import OrganizationLocation

# Create your models here.

class OrganizationLocationRoom(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization_location = models.ForeignKey(OrganizationLocation, on_delete=models.CASCADE)
    archived = models.BooleanField(default=False)
    display_public = models.BooleanField(default=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
