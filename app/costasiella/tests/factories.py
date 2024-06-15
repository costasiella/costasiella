from django.utils import timezone
from django.contrib.auth import get_user_model

import os
import datetime
import factory
import uuid

# Models
from allauth.account.models import EmailAddress
from .. import models

from ..modules.date_tools import last_day_month


class FinanceCostCenterFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.FinanceCostCenter

    archived = False
    name = "First cost center"
    code = 9000


class FinanceInvoiceGroupFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.FinanceInvoiceGroup

    archived = False
    display_public = True
    name = "Another group"
    next_id = 1
    due_after_days = 30
    prefix = 'INV'
    prefix_year = True
    auto_reset_prefix_year = True
    terms = 'Terms here... I guess'
    footer = 'A perfectly formal and normal footer text'
    code = "70"


class FinanceGLAccountFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.FinanceGLAccount

    archived = False
    name = "First glaccount"
    code = 8000


class FinancePaymentBatchCategoryCollectionFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.FinancePaymentBatchCategory

    archived = False
    name = "First collection payment batch category"
    batch_category_type = "COLLECTION"
    description = "hello world"


class FinancePaymentBatchCategoryPaymentFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.FinancePaymentBatchCategory

    archived = False
    name = "First payment payment batch category"
    batch_category_type = "PAYMENT"
    description = "hello world"


class FinancePaymentBatchCollectionInvoicesFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.FinancePaymentBatch

    name = "First invoices batch"
    batch_type = "COLLECTION"
    finance_payment_batch_category = None
    status = "AWAITING_APPROVAL"
    description = "Invoices batch description"
    execution_date = datetime.date(2020, 1, 1)
    include_zero_amounts = False
    note = "Batch note"


class FinancePaymentBatchCollectionCategoryFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.FinancePaymentBatch

    name = "First invoices batch"
    batch_type = "COLLECTION"
    finance_payment_batch_category = factory.SubFactory(FinancePaymentBatchCategoryCollectionFactory)
    status = "AWAITING_APPROVAL"
    description = "Category batch description"
    year = 2020
    month = 1
    execution_date = datetime.date(2020, 1, 1)
    include_zero_amounts = False
    note = "Batch note"


class FinancePaymentMethodFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.FinancePaymentMethod

    archived = False
    system_method = False
    name = "First user defined payment method"
    code = "123456"


class FinanceTaxRateFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.FinanceTaxRate

    archived = False
    name = "BTW 21%"
    percentage = 21
    rate_type = "IN"
    code = "8000"


class OrganizationFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Organization
        django_get_or_create = ('pk',)

    pk = 100
    archived = False
    name = "My Organization"
    branding_color_background = "#f6f6f6"
    branding_color_text = "#333"
    branding_color_accent = "#1ee494"
    branding_color_secondary = "#a9a"


class OrganizationClasstypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OrganizationClasstype

    archived = False
    display_public = True
    name = "First classtype"
    description = "Classtype description"
    url_website = "http://www.costasiella.com"


class OrganizationDiscoveryFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OrganizationDiscovery

    archived = False
    name = "First discovery"


class OrganizationDocumentFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OrganizationDocument

    organization = factory.SubFactory(OrganizationFactory)
    document_type = "TERMS_AND_CONDITIONS"
    version = 1.0
    date_start = datetime.date(2019, 1, 1)
    # date_end is None
    # https://factoryboy.readthedocs.io/en/latest/orms.html
    # Refer to the part "Extra Fields (class dactory.django.FileField)"
    document = factory.django.FileField(
        from_path=os.path.join(os.getcwd(), "costasiella", "tests", "files", "test.pdf"),
    )


class OrganizationDocumentPrivacyPolicyFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OrganizationDocument

    organization = factory.SubFactory(OrganizationFactory)
    document_type = "PRIVACY_POLICY"
    version = 1.0
    date_start = datetime.date(2019, 1, 1)
    # date_end is None
    # https://factoryboy.readthedocs.io/en/latest/orms.html
    # Refer to the part "Extra Fields (class dactory.django.FileField)"
    document = factory.django.FileField(
        from_path=os.path.join(os.getcwd(), "costasiella", "tests", "files", "test.pdf"),
    )


class OrganizationLocationFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OrganizationLocation

    archived = False
    display_public = True
    name = "First location"


class OrganizationLocationRoomFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OrganizationLocationRoom

    organization_location = factory.SubFactory(OrganizationLocationFactory)
    archived = False
    display_public = True
    name = "First location room"


class OrganizationHolidayFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OrganizationHoliday

    name = "First holiday"
    description = "Holiday description here"
    date_start = "1950-01-01"
    date_end = "2999-12-31"
    classes = True


class OrganizationHolidayLocationFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OrganizationHolidayLocation

    organization_location = factory.SubFactory(OrganizationLocationFactory)
    organization_holiday = factory.SubFactory(OrganizationHolidayFactory)


class OrganizationAppointmentCategoryFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OrganizationAppointmentCategory

    archived = False
    display_public = True
    name = "First category"


class OrganizationAppointmentFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OrganizationAppointment

    organization_appointment_category = factory.SubFactory(OrganizationAppointmentCategoryFactory)
    archived = False
    display_public = True
    name = "First appointment"


class OrganizationAnnouncementFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OrganizationAnnouncement

    display_public = True
    display_shop = True
    display_backend = True
    title = "Welcome"
    content = "Welcome to Costasiella!"
    date_start = datetime.date(2020, 1, 1)
    date_end = datetime.date(2999, 12, 31)
    priority = 100


class OrganizationLevelFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OrganizationLevel

    archived = False
    name = "First level"


class OrganizationShiftFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OrganizationShift

    archived = False
    name = "First shift type"


class OrganizationLanguageFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OrganizationLanguage

    archived = False
    name = "NL"


class OrganizationMembershipFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OrganizationMembership

    archived = False
    display_public = True
    display_shop = True
    name = "First membership"
    description = "The first one..."
    price = 12.50
    finance_tax_rate = factory.SubFactory(FinanceTaxRateFactory)
    validity = 1
    validity_unit = "MONTHS"
    terms_and_conditions = "T and C here"
    finance_glaccount = factory.SubFactory(FinanceGLAccountFactory)
    finance_costcenter = factory.SubFactory(FinanceCostCenterFactory)


class OrganizationClasspassFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OrganizationClasspass

    archived = False
    display_public = True
    display_shop = True
    trial_pass = False
    name = "First class pass"
    description = "The first one..."
    price = 125
    finance_tax_rate = factory.SubFactory(FinanceTaxRateFactory)
    validity = 1
    validity_unit = "MONTHS"
    classes = 10
    unlimited = False
    organization_membership = factory.SubFactory(OrganizationMembershipFactory)
    quick_stats_amount = 12.5
    finance_glaccount = factory.SubFactory(FinanceGLAccountFactory)
    finance_costcenter = factory.SubFactory(FinanceCostCenterFactory)


class OrganizationClasspassTrialFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OrganizationClasspass

    archived = False
    display_public = True
    display_shop = True
    trial_pass = True
    name = "One trial class"
    description = "A short description here..."
    price = 15
    finance_tax_rate = factory.SubFactory(FinanceTaxRateFactory)
    validity = 1
    validity_unit = "DAYS"
    classes = 1
    unlimited = False
    quick_stats_amount = 15
    finance_glaccount = factory.SubFactory(FinanceGLAccountFactory)
    finance_costcenter = factory.SubFactory(FinanceCostCenterFactory)


class OrganizationClasspassGroupFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OrganizationClasspassGroup

    name = "First class pass group"
    description = "Description of classpass group here"


class OrganizationClasspassGroupClasspassFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OrganizationClasspassGroupClasspass

    organization_classpass_group = factory.SubFactory(OrganizationClasspassGroupFactory)
    organization_classpass = factory.SubFactory(OrganizationClasspassFactory)


class OrganizationSubscriptionFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OrganizationSubscription

    archived = False
    display_public = True
    display_shop = True
    name = "First subscription"
    description = "The first one..."
    sort_order = 1
    min_duration = 1
    classes = 1
    subscription_unit = "WEEK"
    credit_validity = 62
    reconciliation_classes = 1
    registration_fee = 20
    unlimited = False
    organization_membership = factory.SubFactory(OrganizationMembershipFactory)
    quick_stats_amount = 12.5
    finance_glaccount = factory.SubFactory(FinanceGLAccountFactory)
    finance_costcenter = factory.SubFactory(FinanceCostCenterFactory)


class OrganizationSubscriptionPriceFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OrganizationSubscriptionPrice

    # class Params:
    #     initial_organization_subscription =factory.SubFactory(OrganizationSubscriptionFactory)
    #
    # organization_subscription = factory.LazyAttribute(
    #     lambda o: o.initial_organization_subscription if o.initial_organization_subscription else factory.SubFactory(
    #         OrganizationSubscriptionFactory
    #     )
    # )
    organization_subscription = factory.SubFactory(OrganizationSubscriptionFactory)
    price = 12345
    finance_tax_rate = factory.SubFactory(FinanceTaxRateFactory)
    date_start = '2010-01-01'
    date_end = '2099-12-31'


class OrganizationSubscriptionGroupFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OrganizationSubscriptionGroup

    name = "First subscription group"
    description = "Description here"


class OrganizationSubscriptionGroupSubscriptionFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OrganizationSubscriptionGroupSubscription

    organization_subscription_group = factory.SubFactory(OrganizationSubscriptionGroupFactory)
    organization_subscription = factory.SubFactory(OrganizationSubscriptionFactory)


class OrganizationProductFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OrganizationProduct

    archived = False
    name = "First product"
    description = "Test image"
    price = 10
    finance_tax_rate = factory.SubFactory(FinanceTaxRateFactory)
    finance_glaccount = factory.SubFactory(FinanceGLAccountFactory)
    finance_costcenter = factory.SubFactory(FinanceCostCenterFactory)
    # https://factoryboy.readthedocs.io/en/latest/orms.html
    # Refer to the part "Extra Fields (class dactory.django.FileField)"
    image = factory.django.FileField(
        from_path=os.path.join(os.getcwd(), "costasiella", "tests", "files", "test_image.jpg"),
    )


class AdminUserFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()
    # FACTORY_FOR = get_user_model()

    email = 'admin@costasiellla.com'
    username = 'admin'
    first_name = 'admin'
    last_name = 'user (the boss)'
    password = factory.PostGenerationMethodCall('set_password', 'CSAdmin1#')

    is_superuser = True
    is_staff = True
    is_active = True


class RegularUserFactory(factory.DjangoModelFactory):
    """ Use a uuid in the email field in the tests, as the email address has to be unique.
    This allows multiple calls to the this factory without having to reset the db.
    """
    class Meta:
        model = get_user_model()

    email = '%s@costasiellla.com' % uuid.uuid4()
    first_name = 'user'
    last_name = 'regular user'
    password = factory.PostGenerationMethodCall('set_password', 'CSUser1#')
    organization_discovery = factory.SubFactory(OrganizationDiscoveryFactory)
    organization_language = factory.SubFactory(OrganizationLanguageFactory)
    is_active = True


class InstructorFactory(factory.DjangoModelFactory):
    """ Use a uuid in the email field in the tests, as the email address has to be unique.
    This allows multiple calls to the this factory without having to reset the db.
    """
    class Meta:
        model = get_user_model()

    email = '%s@costasiellla.com' % uuid.uuid4()
    first_name = 'instructor'
    last_name = 'account'
    instructor = True
    password = factory.PostGenerationMethodCall('set_password', 'CSUser1#')

    is_active = True


class Instructor2Factory(factory.DjangoModelFactory):
    """ Use a uuid in the email field in the tests, as the email address has to be unique.
    This allows multiple calls to the this factory without having to reset the db.
    """
    class Meta:
        model = get_user_model()

    email = '%s@costasiellla.com' % uuid.uuid4()
    first_name = 'instructor2'
    last_name = 'account'
    instructor = True
    password = factory.PostGenerationMethodCall('set_password', 'CSUser1#')

    is_active = True


class InstructorProfileFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.AccountInstructorProfile

    account = factory.SubFactory(InstructorFactory)
    classes = True
    appointments = True
    events = True


class AccountDocumentFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.AccountDocument

    account = factory.SubFactory(RegularUserFactory)
    description = "Test file"
    # https://factoryboy.readthedocs.io/en/latest/orms.html
    # Refer to the part "Extra Fields (class dactory.django.FileField)"
    document = factory.django.FileField(
        from_path=os.path.join(os.getcwd(), "costasiella", "tests", "files", "test_image.jpg"),
    )


class BusinessB2BFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Business

    b2b = True
    name = "Great business"
    address = "Businessroad 101"
    postcode = "1234DB"
    city = "B-Town"
    country = "NL"
    phone = "+31612345678"
    phone_2 = "+31612345678"
    email_contact = "contact@business.com"
    email_billing = "billing@business.com"
    registration = "1234DB56"
    tax_registration = "Chamber of Commerce: 1234DB56"


class BusinessSupplierFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Business

    b2b = True
    supplier = True
    name = "Great supplier"
    address = "Businessroad 101"
    postcode = "1234DB"
    city = "B-Town"
    country = "NL"
    phone = "+31612345678"
    phone_2 = "+31612345678"
    email_contact = "contact@business.com"
    email_billing = "billing@business.com"
    registration = "1234DB56"
    tax_registration = "Chamber of Commerce: 1234DB56"


class FinanceExpenseFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.FinanceExpense

    date = datetime.date(2022, 1, 1)
    summary = "test expense summary"
    description = "test expense description"
    amount = 10
    tax = 2.1
    percentage = 90
    supplier = factory.SubFactory(BusinessSupplierFactory)
    finance_glaccount = factory.SubFactory(FinanceGLAccountFactory)
    finance_costcenter = factory.SubFactory(FinanceCostCenterFactory)

    # date_end is None
    # https://factoryboy.readthedocs.io/en/latest/orms.html
    # Refer to the part "Extra Fields (class dactory.django.FileField)"
    document = factory.django.FileField(
        from_path=os.path.join(os.getcwd(), "costasiella", "tests", "files", "test.pdf"),
    )

class FinanceQuoteGroupFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.FinanceQuoteGroup

    archived = False
    display_public = True
    name = "Another group"
    next_id = 1
    expires_after_days = 30
    prefix = 'QUOTE'
    prefix_year = True
    auto_reset_prefix_year = True
    terms = 'Terms here... I guess'
    footer = 'A perfectly formal and normal footer text'
    code = "7000"


class FinanceQuoteFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.FinanceQuote

    account = factory.SubFactory(RegularUserFactory)
    finance_quote_group = factory.SubFactory(FinanceQuoteGroupFactory)
    relation_company = "Company"
    relation_company_registration = "123545ABC"
    relation_company_tax_registration = "12334324BQ"
    relation_contact_name = "Relation name"
    relation_address = "Street 3243"
    relation_postcode = "3423 BF"
    relation_city = "City"
    relation_country = "NL"
    status = "DRAFT"
    summary = "Quote summary"
    note = "Quote note here"


class FinanceQuoteItemFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.FinanceQuoteItem

    finance_quote = factory.SubFactory(FinanceQuoteFactory)
    product_name = "Product"
    description = "Description"
    quantity = 1
    price = 12
    finance_tax_rate = factory.SubFactory(FinanceTaxRateFactory)
    finance_glaccount = factory.SubFactory(FinanceGLAccountFactory)
    finance_costcenter = factory.SubFactory(FinanceCostCenterFactory)


class OrganizationAppointmentPriceFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OrganizationAppointmentPrice

    account = factory.SubFactory(InstructorFactory)
    organization_appointment = factory.SubFactory(OrganizationAppointmentFactory)
    price = 1245
    finance_tax_rate = factory.SubFactory(FinanceTaxRateFactory)


class AllAuthEmailAddress(factory.DjangoModelFactory):
    class Meta:
        model = EmailAddress

    user = factory.SubFactory(RegularUserFactory)
    email = 'user@costasiella.com'
    verified = True
    primary = True


class AccountAcceptedDocumentFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.AccountAcceptedDocument

    account = factory.SubFactory(RegularUserFactory)
    document = factory.SubFactory(OrganizationDocumentFactory)
    date_accepted = datetime.date(2019, 1, 1)


class AccountBankAccountFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.AccountBankAccount

    account = factory.SubFactory(RegularUserFactory)
    number = "123456"
    holder = "First regular user"
    bic = "INGBNL2A"


class AccountBankAccountMandateFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.AccountBankAccountMandate

    account_bank_account = factory.SubFactory(AccountBankAccountFactory)
    reference = "1234-abcd"
    content = "hello world"
    signature_date = datetime.date(2020, 1, 1)


class AccountFinancePaymentBatchCategoryItemFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.AccountFinancePaymentBatchCategoryItem

    account = factory.SubFactory(RegularUserFactory)
    finance_payment_batch_category = factory.SubFactory(FinancePaymentBatchCategoryCollectionFactory)
    year = 2020
    month = 1
    amount = 1234
    description = "hello world"


class AccountSubscriptionFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.AccountSubscription

    account = factory.SubFactory(RegularUserFactory)
    organization_subscription = factory.SubFactory(OrganizationSubscriptionFactory)
    finance_payment_method = factory.SubFactory(FinancePaymentMethodFactory)
    date_start = datetime.date(2019, 1, 1)
    date_end = None
    note = "Subscription note here"
    registration_fee_paid = False


class AccountSubscriptionAltPriceFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.AccountSubscriptionAltPrice

    class Params:
        initial_account_subscription = factory.SubFactory(AccountSubscriptionFactory)

    account_subscription = factory.LazyAttribute(
        lambda o: o.initial_account_subscription if o.initial_account_subscription else factory.SubFactory(
            AccountSubscriptionFactory
        )
    )
    subscription_year = 2019
    subscription_month = 1
    amount = 1
    description = "Test alt price for 2019-01"
    note = "Test alt price note"


class AccountSubscriptionBlockFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.AccountSubscriptionBlock

    account_subscription = factory.SubFactory(AccountSubscriptionFactory)
    date_start = "2019-01-01"
    date_end = "2019-01-31"
    description = "Block test description"


class AccountSubscriptionPauseFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.AccountSubscriptionPause

    account_subscription = factory.SubFactory(AccountSubscriptionFactory)
    date_start = "2019-01-01"
    date_end = "2019-01-31"
    description = "Pause test description"


# class AccountSubscriptionCreditAddFactory(factory.DjangoModelFactory):
#     class Meta:
#         model = models.AccountSubscriptionCredit
#
#     class Params:
#         initial_account_subscription = factory.SubFactory(AccountSubscriptionFactory)
#
#     account_subscription = factory.LazyAttribute(
#         lambda o: o.initial_account_subscription if o.initial_account_subscription else factory.SubFactory(
#             AccountSubscriptionFactory
#         )
#     )
#     description = "Test add mutation"
#     expiration = datetime.date(2099, 12, 31)


class AccountMembershipFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.AccountMembership

    class Params:
        initial_account = factory.SubFactory(RegularUserFactory)

    account = factory.LazyAttribute(
        lambda o: o.initial_account if o.initial_account else factory.SubFactory(RegularUserFactory)
    )
    organization_membership = factory.SubFactory(OrganizationMembershipFactory)
    finance_payment_method = factory.SubFactory(FinancePaymentMethodFactory)
    date_start = datetime.date(2019, 1, 1)
    date_end = datetime.date(2019, 12, 31)
    note = "Membership note here"


class AccountClasspassFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.AccountClasspass

    account = factory.SubFactory(RegularUserFactory)
    organization_classpass = factory.SubFactory(OrganizationClasspassFactory)
    date_start = datetime.date(2019, 1, 1)
    date_end = datetime.date(2019, 3, 31)
    note = "Subscription note here"
    classes_remaining = 10


class AccountNoteBackofficeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.AccountNote

    account = factory.SubFactory(RegularUserFactory)
    note_by = factory.SubFactory(InstructorFactory)
    note_type = "BACKOFFICE"
    note = "Backoffice note"
    injury = False
    processed = False


class FinanceInvoiceFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.FinanceInvoice

    account = factory.SubFactory(RegularUserFactory)
    finance_invoice_group = factory.SubFactory(FinanceInvoiceGroupFactory)
    relation_company = "Company"
    relation_company_registration = "123545ABC"
    relation_company_tax_registration = "12334324BQ"
    relation_contact_name = "Relation name"
    relation_address = "Street 3243"
    relation_postcode = "3423 BF"
    relation_city = "City"
    relation_country = "NL"
    status = "DRAFT"
    summary = "Invoice summary"
    note = "Invoice note here"


class FinanceInvoiceItemFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.FinanceInvoiceItem

    finance_invoice = factory.SubFactory(FinanceInvoiceFactory)
    product_name = "Product"
    description = "Description"
    quantity = 1
    price = 12
    finance_tax_rate = factory.SubFactory(FinanceTaxRateFactory)
    finance_glaccount = factory.SubFactory(FinanceGLAccountFactory)
    finance_costcenter = factory.SubFactory(FinanceCostCenterFactory)


class FinanceInvoicePaymentFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.FinanceInvoicePayment

    class Params:
        initial_invoice = factory.SubFactory(FinanceInvoiceFactory)

    finance_invoice = factory.LazyAttribute(
        lambda o: o.initial_invoice if o.initial_invoice else factory.SubFactory(FinanceInvoiceFactory)
    )
    date = datetime.date(2019, 1, 1)
    amount = 12
    finance_payment_method = factory.SubFactory(FinancePaymentMethodFactory)
    note = "Payment note here!"


class FinancePaymentBatchItemFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.FinancePaymentBatchItem

    finance_payment_batch = factory.SubFactory(FinancePaymentBatchCollectionInvoicesFactory)
    finance_invoice = factory.SubFactory(FinanceInvoiceFactory)
    account = factory.SelfAttribute('finance_invoice.account')
    account_holder = "Test user"
    account_number = "123456"
    account_bic = "NLINGB2A"
    amount = 10
    mandate_signature_date = datetime.date(2020, 1, 1)
    mandate_reference = "Mandate code"
    currency = "EUR"
    description = "Item description"


class FinancePaymentBatchExportFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.FinancePaymentBatchExport

    finance_payment_batch = factory.SubFactory(FinancePaymentBatchCollectionInvoicesFactory)
    account = factory.SubFactory(RegularUserFactory)


class FinanceOrderFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.FinanceOrder

    account = factory.SubFactory(RegularUserFactory)
    status = "RECEIVED"
    message = "Customer's note here..."


class FinanceOrderItemClasspassFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.FinanceOrderItem

    # class Params:
    #     initial_order = factory.SubFactory(FinanceOrderFactory)
    #     initial_organization_classpass = factory.SubFactory(OrganizationClasspassFactory)
    #
    # finance_order = factory.LazyAttribute(
    #     lambda o: o.initial_order if o.initial_order else factory.SubFactory(FinanceOrderFactory)
    # )
    # organization_classpass = factory.LazyAttribute(
    #     lambda o: o.initial_organization_classpass if o.initial_organization_classpass else factory.SubFactory(
    #         OrganizationClasspassFactory
    #     )
    # )
    finance_order = factory.SubFactory(FinanceOrderFactory)
    organization_classpass = factory.SubFactory(OrganizationClasspassFactory)
    product_name = "Classpass"
    description = "Classpass description"
    quantity = 1
    price = factory.SelfAttribute('organization_classpass.price')
    finance_tax_rate = factory.SelfAttribute('organization_classpass.finance_tax_rate')
    finance_glaccount = factory.SelfAttribute('organization_classpass.finance_glaccount')
    finance_costcenter = factory.SelfAttribute('organization_classpass.finance_costcenter')


class SchedulePublicWeeklyClassFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ScheduleItem

    schedule_item_type = "CLASS"
    frequency_type = "WEEKLY"
    frequency_interval = 1  # Monday
    organization_location_room = factory.SubFactory(OrganizationLocationRoomFactory)
    organization_classtype = factory.SubFactory(OrganizationClasstypeFactory)
    organization_level = factory.SubFactory(OrganizationLevelFactory)
    date_start = datetime.date(2014, 1, 1)
    date_end = datetime.date(2099, 12, 31)
    time_start = datetime.time(6, 0)
    time_end = datetime.time(9, 0)
    display_public = True
    spaces = 10
    enrollment_spaces = 10


class SchedulePublicWeeklyClassOTCFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ScheduleItemWeeklyOTC

    schedule_item = factory.SubFactory(SchedulePublicWeeklyClassFactory)
    date = datetime.date(2030, 12, 30)
    description = "Test description"
    account = factory.SubFactory(InstructorFactory)
    role = "SUB"
    account_2 = factory.SubFactory(Instructor2Factory)
    role_2 = "SUB"
    organization_location_room = factory.SelfAttribute('schedule_item.organization_location_room')
    organization_classtype = factory.SelfAttribute('schedule_item.organization_classtype')
    organization_level = factory.SelfAttribute('schedule_item.organization_level')
    time_start = datetime.time(11, 0)
    time_end = datetime.time(12, 30)
    info_mail_enabled = False


class SchedulePublicLastWeekdayOfMonthClassFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ScheduleItem

    schedule_item_type = "CLASS"
    frequency_type = "LAST_WEEKDAY_OF_MONTH"
    frequency_interval = 5  # Friday
    organization_location_room = factory.SubFactory(OrganizationLocationRoomFactory)
    organization_classtype = factory.SubFactory(OrganizationClasstypeFactory)
    organization_level = factory.SubFactory(OrganizationLevelFactory)
    date_start = datetime.date(2014, 1, 1)
    date_end = datetime.date(2099, 12, 31)
    time_start = datetime.time(6, 0)
    time_end = datetime.time(9, 0)
    display_public = True


class ScheduleWeeklyShiftFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ScheduleItem

    schedule_item_type = "SHIFT"
    frequency_type = "WEEKLY"
    frequency_interval = 1  # Monday
    organization_location_room = factory.SubFactory(OrganizationLocationRoomFactory)
    organization_shift = factory.SubFactory(OrganizationShiftFactory)
    date_start = datetime.date(2014, 1, 1)
    date_end = datetime.date(2099, 12, 31)
    time_start = datetime.time(6, 0)
    time_end = datetime.time(9, 0)


class ScheduleWeeklyShiftOTCFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ScheduleItemWeeklyOTC

    schedule_item = factory.SubFactory(ScheduleWeeklyShiftFactory)
    date = datetime.date(2030, 12, 30)
    description = "Test description"
    account = factory.SubFactory(InstructorFactory)
    account_2 = factory.SubFactory(Instructor2Factory)
    organization_location_room = factory.SelfAttribute('schedule_item.organization_location_room')
    organization_shift = factory.SelfAttribute('schedule_item.organization_shift')
    time_start = datetime.time(11, 0)
    time_end = datetime.time(12, 30)


class ScheduleItemAttendanceClasspassFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ScheduleItemAttendance

    account_classpass = factory.SubFactory(AccountClasspassFactory)
    account = factory.SelfAttribute('account_classpass.account')
    schedule_item = factory.SubFactory(SchedulePublicWeeklyClassFactory)
    attendance_type = 'CLASSPASS'
    date = datetime.date(2030, 12, 30)
    online_booking = False
    booking_status = "ATTENDING"


class ScheduleItemAttendanceSubscriptionFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ScheduleItemAttendance

    account_subscription = factory.SubFactory(AccountSubscriptionFactory)
    account = factory.SelfAttribute('account_subscription.account')
    schedule_item = factory.SubFactory(SchedulePublicWeeklyClassFactory)
    attendance_type = 'SUBSCRIPTION'
    date = datetime.date(2030, 12, 30)
    online_booking = False
    booking_status = "ATTENDING"


class ScheduleItemEnrollmentFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ScheduleItemEnrollment

    account_subscription = factory.SubFactory(AccountSubscriptionFactory)
    schedule_item = factory.SubFactory(SchedulePublicWeeklyClassFactory)
    date_start = datetime.date(2010, 1, 1)
    date_end = datetime.date(2999, 12, 30)


class AccountSubscriptionCreditAttendanceFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.AccountSubscriptionCredit

    schedule_item_attendance = factory.SubFactory(ScheduleItemAttendanceSubscriptionFactory)
    account_subscription = factory.SelfAttribute('schedule_item_attendance.account_subscription')
    expiration = datetime.date(2099, 12, 31)
    description = "Test AccountSubscription credit"

class AccountSubscriptionCreditFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.AccountSubscriptionCredit

    account_subscription = factory.SubFactory(AccountSubscriptionFactory)
    expiration = datetime.date(2099, 12, 31)
    description = "Test AccountSubscription credit"


class ScheduleEventFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ScheduleEvent

    archived = False
    display_public = True
    display_shop = True
    auto_send_info_mail = False
    organization_location = factory.SubFactory(OrganizationLocationFactory)
    name = "Test event"
    tagline = "A catching tagline"
    preview = "Beautiful event preview"
    description = "Extensive description"
    organization_level = factory.SubFactory(OrganizationLevelFactory)
    instructor = factory.SubFactory(InstructorFactory)
    instructor_2 = factory.SubFactory(Instructor2Factory)
    info_mail_content = "Hello world from the info mail field"


class ScheduleEventFullTicketFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ScheduleEventTicket

    schedule_event = factory.SubFactory(ScheduleEventFactory)
    full_event = True
    deletable = False
    display_public = True
    name = "Full event"
    description = "Full event ticket"
    price = 100
    finance_tax_rate = factory.SubFactory(FinanceTaxRateFactory)
    finance_glaccount = factory.SubFactory(FinanceGLAccountFactory)
    finance_costcenter = factory.SubFactory(FinanceCostCenterFactory)


class AccountScheduleEventTicketFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.AccountScheduleEventTicket

    account = factory.SubFactory(RegularUserFactory)
    schedule_event_ticket = factory.SubFactory(ScheduleEventFullTicketFactory)
    cancelled = False
    payment_confirmation = False
    info_mail_sent = False


class AccountProductFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.AccountProduct

    account = factory.SubFactory(RegularUserFactory)
    organization_product = factory.SubFactory(OrganizationProductFactory)
    quantity = 1


class ScheduleEventMediaFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ScheduleEventMedia

    schedule_event = factory.SubFactory(ScheduleEventFactory)
    sort_order = 0
    description = "Test image"
    # https://factoryboy.readthedocs.io/en/latest/orms.html
    # Refer to the part "Extra Fields (class dactory.django.FileField)"
    image = factory.django.FileField(
        from_path=os.path.join(os.getcwd(), "costasiella", "tests", "files", "test_image.jpg"),
    )


class ScheduleEventEarlybirdFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ScheduleEventEarlybird

    schedule_event = factory.SubFactory(ScheduleEventFactory)
    date_start = datetime.date(2020, 1, 1)
    date_end = datetime.date(2999, 12, 31)
    discount_percentage = 10


class ScheduleEventSubscriptionGroupDiscountFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ScheduleEventSubscriptionGroupDiscount

    schedule_event = factory.SubFactory(ScheduleEventFactory)
    organization_subscription_group = factory.SubFactory(OrganizationSubscriptionGroupFactory)
    discount_percentage = 10


class ScheduleItemEventActivityFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ScheduleItem

    schedule_event = factory.SubFactory(ScheduleEventFactory)
    schedule_item_type = "EVENT_ACTIVITY"
    frequency_type = "SPECIFIC"
    frequency_interval = 0
    organization_location_room = factory.SubFactory(OrganizationLocationRoomFactory)
    date_start = datetime.date(2014, 1, 1)
    time_start = datetime.time(6, 0)
    time_end = datetime.time(9, 0)
    display_public = True
    account = factory.SelfAttribute('schedule_event.instructor')
    account_2 = factory.SelfAttribute('schedule_event.instructor_2')
    name = "Event activity 1"
    spaces = 20


class ScheduleItemAttendanceScheduleEventFactory(factory.DjangoModelFactory):
    """ Usage
    account_schedule_event_ticket and schedule_item have to be specified when using factory
    """
    class Meta:
        model = models.ScheduleItemAttendance

    account = factory.SelfAttribute('account_schedule_event_ticket.account')
    attendance_type = 'SCHEDULE_EVENT_TICKET'
    date = factory.SelfAttribute('schedule_item.date_start')
    online_booking = False
    booking_status = "ATTENDING"


class ScheduleEventTicketScheduleItemIncludedFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ScheduleEventTicketScheduleItem

    included = True


class ScheduleItemAccountFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ScheduleItemAccount

    schedule_item = factory.SubFactory(SchedulePublicWeeklyClassFactory)
    account = factory.SubFactory(InstructorFactory)
    account_2 = factory.SubFactory(Instructor2Factory)
    role_2 = "ASSISTANT"
    date_start = datetime.date(2014, 1, 1)


class ScheduleItemPriceFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ScheduleItemPrice

    class Params:
        initial_schedule_item = factory.SubFactory(SchedulePublicWeeklyClassFactory)

    schedule_item = factory.LazyAttribute(
        lambda o: o.initial_schedule_item if o.initial_schedule_item else factory.SubFactory(SchedulePublicWeeklyClassFactory)
    )
    organization_classpass_dropin = factory.SubFactory(OrganizationClasspassFactory)
    organization_classpass_trial = factory.SubFactory(OrganizationClasspassTrialFactory)
    date_start = datetime.date(2014, 1, 1)


class ScheduleItemOrganizationSubscriptionGroupDenyFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ScheduleItemOrganizationSubscriptionGroup

    class Params:
        initial_schedule_item = factory.SubFactory(SchedulePublicWeeklyClassFactory)

    schedule_item = factory.LazyAttribute(
        lambda o: o.initial_schedule_item if o.initial_schedule_item else factory.SubFactory(SchedulePublicWeeklyClassFactory)
    )
    organization_subscription_group = factory.SubFactory(OrganizationSubscriptionGroupFactory)
    enroll = False
    shop_book = False
    attend = False


class ScheduleItemOrganizationSubscriptionGroupAllowFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ScheduleItemOrganizationSubscriptionGroup

    class Params:
        initial_schedule_item = factory.SubFactory(SchedulePublicWeeklyClassFactory)

    schedule_item = factory.LazyAttribute(
        lambda o: o.initial_schedule_item if o.initial_schedule_item else factory.SubFactory(SchedulePublicWeeklyClassFactory)
    )
    organization_subscription_group = factory.SubFactory(OrganizationSubscriptionGroupFactory)
    enroll = True
    shop_book = True
    attend = True


class ScheduleItemOrganizationClasspassGroupDenyFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ScheduleItemOrganizationClasspassGroup


    class Params:
        initial_schedule_item = factory.SubFactory(SchedulePublicWeeklyClassFactory)

    schedule_item = factory.LazyAttribute(
        lambda o: o.initial_schedule_item if o.initial_schedule_item
            else factory.SubFactory(SchedulePublicWeeklyClassFactory)
    )
    organization_classpass_group = factory.SubFactory(OrganizationClasspassGroupFactory)
    shop_book = False
    attend = False


class ScheduleItemOrganizationClasspassGroupAllowFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ScheduleItemOrganizationClasspassGroup

    class Params:
        initial_schedule_item = factory.SubFactory(SchedulePublicWeeklyClassFactory)

    schedule_item = factory.LazyAttribute(
        lambda o: o.initial_schedule_item if o.initial_schedule_item
            else factory.SubFactory(SchedulePublicWeeklyClassFactory)
    )
    organization_classpass_group = factory.SubFactory(OrganizationClasspassGroupFactory)
    shop_book = True
    attend = True


class InsightAccountInactiveFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.InsightAccountInactive

    no_activity_after_date = timezone.now().date()


class InsightAccountInactiveAccountFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.InsightAccountInactiveAccount

    account = factory.SubFactory(RegularUserFactory)
    insight_account_inactive = factory.SubFactory(InsightAccountInactiveFactory)


class SystemMailChimpListFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.SystemMailChimpList

    name = "Newsletter"
    description = "A short description of our newsletter"
    frequency = "Once or twice a month"
    mailchimp_list_id = "abc124f0"


class SystemMailTemplateFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.SystemMailTemplate

    name = "Test"
    subject = "Test subject"
    title = "Test title"
    description = "Test description"
    content = "Test content"
    comments = "Test comments"


class SystemNotificationFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.SystemNotification

    name = "Newsletter"
    system_mail_template = factory.SubFactory(SystemMailTemplateFactory)


class SystemNotificationAccountFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.SystemNotificationAccount

    account = factory.SubFactory(RegularUserFactory)
    system_notification = factory.SubFactory(SystemNotificationFactory)


class SystemSettingFinanceCurrencyFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.SystemSetting

    setting = "finance_currency"
    value = "EUR"


