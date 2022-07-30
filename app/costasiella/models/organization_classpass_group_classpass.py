from django.db import models

from .organization_classpass import OrganizationClasspass
from .organization_classpass_group import OrganizationClasspassGroup
from .helpers import model_string


class OrganizationClasspassGroupClasspass(models.Model):
    organization_classpass_group = models.ForeignKey(OrganizationClasspassGroup, on_delete=models.CASCADE)
    organization_classpass = models.ForeignKey(OrganizationClasspass, on_delete=models.CASCADE)

    def __str__(self):
        return model_string(self)
