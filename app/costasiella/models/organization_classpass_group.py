from django.db import models

from .organization_classpass import OrganizationClasspass

class OrganizationClasspassGroup(models.Model):
    archived = models.BooleanField(default=False)
    name = models.CharField(max_length=255, unique=True)
    organization_classpasses = models.ManyToManyField(OrganizationClasspass, through='OrganizationClasspassGroupClasspass', related_name='classpasses')

    def __str__(self):
        return self.name
    
