import uuid

from django.db import models

# Create your models here.

class SchoolLocation(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    archived = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    display_public = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
from django import forms

class SchoolLocationForm(forms.ModelForm):
    class Meta:
        model = SchoolLocation
        fields = ('name', 'display_public')