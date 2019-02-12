import uuid

from django.db import models

# Create your models here.

class SchoolLocation(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    archived = models.BooleanField(default=False)
    name = models.CharField(max_length=200)
    public = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
