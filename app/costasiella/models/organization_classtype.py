import uuid

from django.db import models
from sorl.thumbnail import ImageField


# Create your models here.
class OrganizationClasstype(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    archived = models.BooleanField(default=False)
    display_public = models.BooleanField(default=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    url_website = models.URLField()
    image = ImageField(upload_to='organization_classtype', default=None)

    def __str__(self):
        return self.name
