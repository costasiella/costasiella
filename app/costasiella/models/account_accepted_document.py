from django.db import models


from .account import Account
from .organization_document import OrganizationDocument
from ..modules.encrypted_fields import EncryptedTextField


class AccountAcceptedDocument(models.Model):
    # add additional fields in here
    # instructor and employee will use OneToOne fields. An account can optionally be a instructor or employee.
    # Editable parameter docs
    # https://docs.djangoproject.com/en/2.2/ref/models/fields/#editable

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="accepted_documents")
    document = models.ForeignKey(OrganizationDocument, on_delete=models.SET_NULL, null=True)
    date_accepted = models.DateTimeField(auto_now_add=True, editable=False)
    client_ip = EncryptedTextField(default="")
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.document.document_type + ' [' + str(self.date_accepted) + ']'
