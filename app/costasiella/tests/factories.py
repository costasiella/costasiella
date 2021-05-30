from django.utils import timezone
from django.contrib.auth import get_user_model

import os
import datetime
import factory

# Models
from allauth.account.models import EmailAddress
from .. import models

from ..modules.date_tools import last_day_month


class FinanceCostCenterFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.FinanceCostCenter

    archived = False
    name = "First cost center"
    code = "9000"


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
    footer = 'A prefectly formal and normal footer text'
    code = "70"


class FinanceGLAccountFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.FinanceGLAccount

    archived = False
    name = "First glaccount"
    code = "8000"


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


class OrganizationLevelFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OrganizationLevel

    archived = False
    name = "First level"


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
    trial_times = 1
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

    archived = False
    name = "First class pass group"


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
    credit_validity = 1
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

    archived = False
    name = "First subscription group"


class OrganizationSubscriptionGroupSubscriptionFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OrganizationSubscriptionGroupSubscription

    organization_subscription_group = factory.SubFactory(OrganizationSubscriptionGroupFactory)
    organization_subscription = factory.SubFactory(OrganizationSubscriptionFactory)


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
    class Meta:
        model = get_user_model()
    # FACTORY_FOR = get_user_model()

    email = 'user@costasiellla.com'
    username = 'regular_user'
    first_name = 'user'
    last_name = 'regular user'
    password = factory.PostGenerationMethodCall('set_password', 'CSUser1#')

    is_active = True


class TeacherFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()
    # FACTORY_FOR = get_user_model()

    email = 'user@costasiellla.com'
    username = 'teacher'
    first_name = 'teacher'
    last_name = 'account'
    teacher = True
    password = factory.PostGenerationMethodCall('set_password', 'CSUser1#')

    is_active = True


class Teacher2Factory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()
    # FACTORY_FOR = get_user_model()

    email = 'user@costasiellla.com'
    username = 'teacher2'
    first_name = 'teacher2'
    last_name = 'account'
    teacher = True
    password = factory.PostGenerationMethodCall('set_password', 'CSUser1#')

    is_active = True


class TeacherProfileFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.AccountTeacherProfile

    account = factory.SubFactory(TeacherFactory)
    classes = True
    appointments = True
    events = True


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


class OrganizationAppointmentPriceFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OrganizationAppointmentPrice

    account = factory.SubFactory(TeacherFactory)
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
        model = models.AccountBankAccountMandate

    account = factory.SubFactory(RegularUserFactory)
    finance_payment_batch_category = factory.SubFactory(FinancePaymentBatchCategoryCollectionFactory)
    year = 2020
    month = 1
    amount = 1234
    description = "hello world"


class AccountSubscriptionFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.AccountSubscription

    class Params:
        initial_account = factory.SubFactory(RegularUserFactory)

    account = factory.LazyAttribute(
        lambda o: o.initial_account if o.initial_account else factory.SubFactory(RegularUserFactory)
    )
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

    class Params:
        initial_account_subscription = factory.SubFactory(AccountSubscriptionFactory)

    account_subscription = factory.LazyAttribute(
        lambda o: o.initial_account_subscription if o.initial_account_subscription else factory.SubFactory(
            AccountSubscriptionFactory
        )
    )
    date_start = "2019-01-01"
    date_end = "2019-01-31"
    description = "Block test description"


class AccountSubscriptionPauseFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.AccountSubscriptionPause

    class Params:
        initial_account_subscription = factory.SubFactory(AccountSubscriptionFactory)

    account_subscription = factory.LazyAttribute(
        lambda o: o.initial_account_subscription if o.initial_account_subscription else factory.SubFactory(
            AccountSubscriptionFactory
        )
    )
    date_start = "2019-01-01"
    date_end = "2019-01-31"
    description = "Pause test description"


class AccountSubscriptionCreditAddFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.AccountSubscriptionCredit

    class Params:
        initial_account_subscription = factory.SubFactory(AccountSubscriptionFactory)

    account_subscription = factory.LazyAttribute(
        lambda o: o.initial_account_subscription if o.initial_account_subscription else factory.SubFactory(
            AccountSubscriptionFactory
        )
    )
    mutation_type = "ADD"
    mutation_amount = 10
    description = "Test add mutation"


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

    class Params:
        initial_account = factory.SubFactory(RegularUserFactory)

    account = factory.LazyAttribute(
        lambda o: o.initial_account if o.initial_account else factory.SubFactory(RegularUserFactory)
    )
    organization_classpass = factory.SubFactory(OrganizationClasspassFactory)
    date_start = datetime.date(2019, 1, 1)
    date_end = datetime.date(2019, 3, 31)
    note = "Subscription note here"
    classes_remaining = 10
    

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


class FinanceOrderFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.FinanceOrder

    class Params:
        initial_account = factory.SubFactory(RegularUserFactory)

    account = factory.LazyAttribute(
        lambda o: o.initial_account if o.initial_account else factory.SubFactory(RegularUserFactory)
    )
    status = "RECEIVED"
    message = "Customer's note here..."


class FinanceOrderItemClasspassFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.FinanceOrderItem

    class Params:
        initial_order = factory.SubFactory(FinanceOrderFactory)
        initial_organization_classpass = factory.SubFactory(OrganizationClasspassFactory)

    finance_order = factory.LazyAttribute(
        lambda o: o.initial_order if o.initial_order else factory.SubFactory(FinanceOrderFactory)
    )
    organization_classpass = factory.LazyAttribute(
        lambda o: o.initial_organization_classpass if o.initial_organization_classpass else factory.SubFactory(
            OrganizationClasspassFactory
        )
    )
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
    

class SchedulePublicWeeklyClassOTCFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ScheduleItemWeeklyOTC

    schedule_item = factory.SubFactory(SchedulePublicWeeklyClassFactory)
    date = datetime.date(2030, 12, 30)
    description = "Test description"
    account = factory.SubFactory(TeacherFactory)
    role = "SUB"
    account_2 = factory.SubFactory(Teacher2Factory)
    role_2 = "SUB"
    organization_location_room = factory.SelfAttribute('schedule_item.organization_location_room')
    organization_classtype = factory.SelfAttribute('schedule_item.organization_classtype')
    organization_level = factory.SelfAttribute('schedule_item.organization_level')
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


class AccountSubscriptionCreditAttendanceSubFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.AccountSubscriptionCredit

    schedule_item_attendance = factory.SubFactory(ScheduleItemAttendanceSubscriptionFactory)
    account_subscription = factory.SelfAttribute('schedule_item_attendance.account_subscription')
    mutation_type = "SUB"
    mutation_amount = 1
    description = "Test subscription SUB mutation"


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
    teacher = factory.SubFactory(TeacherFactory)
    teacher_2 = factory.SubFactory(Teacher2Factory)
    info_mail_content = "Hello world from the info mail field"


class ScheduleEventFullTicketFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ScheduleEventTicket

    class Params:
        initial_schedule_event = factory.SubFactory(ScheduleEventFactory)

    schedule_event = factory.LazyAttribute(
        lambda o: o.initial_schedule_event if o.initial_schedule_event else factory.SubFactory(ScheduleEventFactory)
    )
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


class ScheduleEventMediaFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ScheduleEventMedia

    class Params:
        initial_schedule_event = factory.SubFactory(ScheduleEventFactory)

    schedule_event = factory.LazyAttribute(
        lambda o: o.initial_schedule_event if o.initial_schedule_event else factory.SubFactory(ScheduleEventFactory)
    )
    sort_order = 0
    description = "Test image"
    # https://factoryboy.readthedocs.io/en/latest/orms.html
    # Refer to the part "Extra Fields (class dactory.django.FileField)"
    image = factory.django.FileField(
        from_path=os.path.join(os.getcwd(), "costasiella", "tests", "files", "test_image.jpg"),
    )


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
    account = factory.SelfAttribute('schedule_event.teacher')
    account_2 = factory.SelfAttribute('schedule_event.teacher_2')
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

    
class ScheduleItemTeacherFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ScheduleItemTeacher

    schedule_item = factory.SubFactory(SchedulePublicWeeklyClassFactory)
    account = factory.SubFactory(TeacherFactory)
    account_2 = factory.SubFactory(Teacher2Factory)
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
        lambda o: o.initial_schedule_item if o.initial_schedule_item else factory.SubFactory(SchedulePublicWeeklyClassFactory)
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
        lambda o: o.initial_schedule_item if o.initial_schedule_item else factory.SubFactory(SchedulePublicWeeklyClassFactory)
    )
    organization_classpass_group = factory.SubFactory(OrganizationClasspassGroupFactory)
    shop_book = True
    attend = True


class SystemSettingFinanceCurrencyFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.SystemSetting

    setting = "finance_currency"
    value = "EUR"


