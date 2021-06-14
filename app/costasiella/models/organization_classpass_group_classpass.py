from django.db import models

from .organization_classpass import OrganizationClasspass
from .organization_classpass_group import OrganizationClasspassGroup


class OrganizationClasspassGroupClasspass(models.Model):
    organization_classpass_group = models.ForeignKey(OrganizationClasspassGroup, on_delete=models.CASCADE)
    organization_classpass = models.ForeignKey(OrganizationClasspass, on_delete=models.CASCADE)

    def __str__(self):
        return self.organization_classpass_group.name + ' ' + self.organization_classpass.name

