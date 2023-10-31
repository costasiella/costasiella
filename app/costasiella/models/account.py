from django.utils.translation import gettext as _

from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import models
from sorl.thumbnail import ImageField

from allauth.account.models import EmailAddress
from .business import Business
from .organization_discovery import OrganizationDiscovery
from .organization_language import OrganizationLanguage

from ..modules.encrypted_fields import EncryptedTextField
from .choices.account_country_codes import get_account_country_codes
from .choices.account_genders import get_account_genders

from .helpers import model_string


class Account(AbstractUser):
    # add additional fields in here
    # instructor and employee will use OneToOne fields. An account can optionally be a instructor or employee.
    # Editable parameter docs
    # https://docs.djangoproject.com/en/2.2/ref/models/fields/#editable

    class Meta:
        permissions = [
            ('view_automation', _("Can view automation menu")),
            ('view_insight', _("Can view insight menu")),
            ('view_insightaccountsinactive', _("Can view insight accounts inactive")),
            ('view_insightclasspasses', _("Can view insight classpasses active")),
            ('view_insightfinanceinvoicesopenondate', _("Can view insight finance invoices open on date")),
            ('view_insightfinancetaxratesummary', _("Can view insight finance tax rates summary")),
            ('view_insightinstructorclassesmonth', _("Can view insight instructor classes in month")),
            ('view_insightkeynumberswosubscription', _("Can view insight key numbers without subscription")),
            ('view_insightrevenue', _("Can view insight subscriptions sold")),
            ('view_insightsubscriptions', _("Can view insight subscriptions")),
            ('view_insighttrialpasses', _("Can view insight trial passes")),
            ('view_selfcheckin', _("Can use the selfcheckin feature")),
        ]

    # Ensure email is unique
    email = models.EmailField(_('email address'), unique=True)
    gender_choices = get_account_genders()
    country_choices = get_account_country_codes()

    customer = models.BooleanField(default=True)
    instructor = models.BooleanField(default=False)
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
    image = ImageField(upload_to='account', default=None)
    invoice_to_business = models.ForeignKey(
        Business, null=True, on_delete=models.SET_NULL, related_name="accounts"
    )
    mollie_customer_id = models.CharField(max_length=255, default="", editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Account: {self.email} ({self.id})"

    def save(self, *args, **kwargs):
        name = [self.first_name, self.last_name]
        self.full_name = " ".join(name)
        if not self.username:
            self.username = self.email
        super(Account, self).save(*args, **kwargs)

    def new_account_setup(self):
        self.create_allauth_email()
        self.create_bank_account()
        self.create_instructor_profile()

    def create_allauth_email(self):
        email_address = EmailAddress.objects.filter(user=self)

        if not email_address:
            email_address = EmailAddress(
                user=self,
                email=self.email,
                verified=True,
                primary=True
            )
            email_address.save()

    def create_bank_account(self):
        from .account_bank_account import AccountBankAccount

        account_bank_account = AccountBankAccount.objects.filter(account=self)

        if not account_bank_account:
            account_bank_account = AccountBankAccount(
                account=self
            )
            account_bank_account.save()

    def create_instructor_profile(self):
        from .account_instructor_profile import AccountInstructorProfile

        instructor_profile = AccountInstructorProfile.objects.filter(account=self)

        if not instructor_profile:
            instructor_profile = AccountInstructorProfile(
                account=self
            )
            instructor_profile.save()

        return instructor_profile

    def has_bank_account_info(self):
        """
        True if at least account holder & number are filled for the accounts' bank account
        :return: boolean
        """
        from .account_bank_account import AccountBankAccount

        account_bank_accounts = AccountBankAccount.objects.filter(account=self)

        has_info = False
        if account_bank_accounts.exists():
            account_bank_account = account_bank_accounts.first()
            if account_bank_account.number and account_bank_account.holder:
                has_info = True

        return has_info

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

    def has_paid_subscription_registration_fee(self):
        """
        Check if this account has ever paid a registration fee
        :return: boolean
        """
        from .account_subscription import AccountSubscription

        qs = AccountSubscription.objects.filter(
            account=self,
            registration_fee_paid=True
        )
        has_paid_registration_fee = False
        if qs.exists():
            has_paid_registration_fee = True

        return has_paid_registration_fee

    def get_profile_policy(self):
        from ..dudes import SystemSettingDude

        system_setting_dude = SystemSettingDude()
        policy = system_setting_dude.get("shop_account_profile_required_fields") or "MINIMUM"

        return policy

    def has_complete_enough_profile(self):
        """
        Check whether the minimum required fields by the profile setting are filled
        """
        from ..dudes import SystemSettingDude

        system_setting_dude = SystemSettingDude()
        policy = system_setting_dude.get("shop_account_profile_required_fields") or "MINIMUM"

        profile_is_complete_enough = True
        # These checks are required for all policies
        if not self.first_name or not self.last_name or not self.email:
            profile_is_complete_enough = False

        # Only do these checks when the policy is set to CONTACT
        if policy == "CONTACT":
            if (not self.address or
                not self.postcode or
                not self.city or
                not self.country or
                not (self.phone or self.mobile)
                ):
                profile_is_complete_enough = False

        return profile_is_complete_enough

    def get_mailchimp_email_hash(self):
        """
            Return email hash (required for MailChimp integration)
        """
        import hashlib

        md5 = hashlib.md5()
        md5.update(str.encode(self.email.lower()))

        return md5.hexdigest()

    # @property
    # def has_active_subscription(self, date=None):
    #     from .account_subscription import AccountSubscription
    #
    #     if not date:
    #         now = timezone.now()
    #         date = now.date()
    #
    #     qs = AccountSubscription.objects.filter(
    #         Q(account=self),
    #         Q(date_start__lte=date),
    #         (Q(date_end__gte=date) | Q(date_end__isnull=True))
    #     )
    #
    #     # True if account has an active subscription, false if not.
    #     return qs.exists()
