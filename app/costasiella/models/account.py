from django.utils.translation import gettext as _

from django.contrib.auth.models import AbstractUser
from django.db import models

from allauth.account.models import EmailAddress
from .organization_discovery import OrganizationDiscovery
from .organization_language import OrganizationLanguage

from ..modules.encrypted_fields import EncryptedTextField
from .choices.account_country_codes import get_account_country_codes
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

    # Ensure email is unique
    email = models.EmailField(_('email address'), unique=True)
    gender_choices = get_account_genders()
    country_choices = get_account_country_codes()

    customer = models.BooleanField(default=True)
    teacher = models.BooleanField(default=False)
    employee = models.BooleanField(default=False)
    full_name = models.CharField(max_length=255, default="", editable=False)
    gender = EncryptedTextField(default="")
    date_of_birth = EncryptedTextField(data_type="date", default="")
    address = EncryptedTextField(default="")
    postcode = EncryptedTextField(default="")
    city = EncryptedTextField(default="")
    country = EncryptedTextField(default="")
    phone = EncryptedTextField(default="")
    mobile = EncryptedTextField(default="")
    emergency = EncryptedTextField(default="")
    key_number = EncryptedTextField(default="")
    organization_discovery = models.ForeignKey(
        OrganizationDiscovery, null=True, on_delete=models.SET_NULL, related_name="accounts"
    )
    organization_language = models.ForeignKey(
        OrganizationLanguage, null=True, on_delete=models.SET_NULL, related_name="accounts"
    )
    mollie_customer_id = models.CharField(max_length=255, default="", editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Account: %s" % self.email

    def save(self, *args, **kwargs):
        name = [self.first_name, self.last_name]
        self.full_name = " ".join(name)
        if not self.username:
            self.username = self.email
        super(Account, self).save(*args, **kwargs)

    def create_allauth_email(self):
        email_address = EmailAddress(
            user=self,
            email=self.email,
            verified=True,
            primary=True
        )
        email_address.save()

    def create_bank_account(self):
        from .account_bank_account import AccountBankAccount

        account_bank_account = AccountBankAccount(
            account=self
        )
        account_bank_account.save()

    def create_teacher_profile(self):
        from .account_teacher_profile import AccountTeacherProfile

        account_teacher_profile = AccountTeacherProfile(
            account=self
        )
        account_teacher_profile.save()

        return account_teacher_profile

    def has_reached_trial_limit(self):
        """
        True if trial limit has been reached, otherwise false
        :return: boolean
        """
        from ..dudes import SystemSettingDude
        from .account_classpass import AccountClasspass

        system_setting_dude = SystemSettingDude()
        trial_pass_limit = system_setting_dude.get("workflow_trial_pass_limit") or 1
        trial_pass_limit = int(trial_pass_limit)

        count_trial_passes = AccountClasspass.objects.filter(
            account=self,
            organization_classpass__trial_pass=True
        ).count()

        return count_trial_passes >= trial_pass_limit
