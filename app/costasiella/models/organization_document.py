from django.utils.translation import gettext as _

from django.db import models

from .organization import Organization
from .choices.organization_document_types import get_organization_document_types


class OrganizationDocument(models.Model):
    DOCUMENT_TYPES = get_organization_document_types()

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    version = models.CharField(max_length=50, default="")
    date_start = models.DateField()
    date_end = models.DateField(null=True)
    document = models.FileField(upload_to='organization_document', default=None)

    class Meta:
        ordering = ['-date_start']
    
    def __str__(self):
        return self.document_type + ' ' + self.document.url
