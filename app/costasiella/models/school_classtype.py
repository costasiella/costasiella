import uuid

from django.db import models

# Create your models here.

class SchoolClasstype(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    archived = models.BooleanField(default=False)
    display_public = models.BooleanField(default=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    url_website = models.URLField()
    image = models.ImageField(default=None, upload_to='costasiella/media/school_classtype_images')
    
    def __str__(self):
        return self.name
    
from django import forms
