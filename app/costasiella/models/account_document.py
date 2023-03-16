from django.utils.translation import gettext as _

from django.db import models

from .account import Account
from .organization import Organization
from .choices.organization_document_types import get_organization_document_types
from django.conf import settings
from .helpers import model_string


class AccountDocument(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="documents")
    description = models.CharField(max_length=255, default="")
    document = models.FileField(upload_to='account_document', default=None, storage=settings.MEDIA_PROTECTED_STORAGE)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    # class Meta:
    #     ordering = ['-date_start']
    
    def __str__(self):
        return model_string(self)