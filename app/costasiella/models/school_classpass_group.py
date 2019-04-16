from django.db import models

from .school_classpass import SchoolClasspass

class SchoolClasspassGroup(models.Model):
    archived = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    classpasses = models.ManyToManyField(SchoolClasspass, through='SchoolClasspassGroupClasspass', related_name='classpasses')

    def __str__(self):
        return self.name
    
