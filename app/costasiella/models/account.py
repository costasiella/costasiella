from django.utils.translation import gettext as _

from django.contrib.auth.models import AbstractUser
from django.db import models

from ..modules.encrypted_fields import EncryptedTextField
from .choices.account_genders import get_account_genders


class Account(AbstractUser):
    # add additional fields in here
    # teacher and employee will use OneToOne fields. An account can optionally be a teacher or employee.
    # Editable parameter docs
    # https://docs.djangoproject.com/en/2.2/ref/models/fields/#editable

    class Meta:
        permissions = [
            ('view_automation', _("Can view automation menu")),
            ('view_insight', _("Can view insight menu")),
            ('view_insightclasspassesactive', _("Can view insight classpasses active")),
            ('view_insightclasspassessold', _("Can view insight classpasses sold")),
            ('view_insightsubscriptionsactive', _("Can view insight subscriptions active")),
            ('view_insightsubscriptionssold', _("Can view insight subscriptions sold")),
            ('view_selfcheckin', _("Can use the selfcheckin feature")),
        ]

    gender_choices = get_account_genders()

    customer = models.BooleanField(default=True)
    teacher = models.BooleanField(default=False)
    employee = models.BooleanField(default=False)
    full_name = models.CharField(max_length=255, default="", editable=False)
    gender = EncryptedTextField(default="", choices=gender_choices)
    date_of_birth = EncryptedTextField(data_type="date", default="")
    address = EncryptedTextField(default="")
    postcode = EncryptedTextField(default="")
    city = EncryptedTextField(default="")
    country = EncryptedTextField(default="")
    phone = EncryptedTextField(default="")
    mobile = EncryptedTextField(default="")
    emergency = EncryptedTextField(default="")
    mollie_customer_id = models.CharField(max_length=255, default="", editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Account: %s" % self.email

    def save(self, *args, **kwargs):
        name = [self.first_name, self.last_name]
        self.full_name = " ".join(name)
        super(Account, self).save(*args, **kwargs)