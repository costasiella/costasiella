from django.db import models

from .organization_classpass import OrganizationClasspass


class OrganizationClasspassGroup(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(default="")
    organization_classpasses = models.ManyToManyField(OrganizationClasspass,
                                                      through='OrganizationClasspassGroupClasspass',
                                                      related_name='classpasses')

    def __str__(self):
        return self.name
