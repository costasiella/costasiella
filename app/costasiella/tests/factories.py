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

    id = 100
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
    name = "First class pass"
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

    class Params:
        initial_account = factory.SubFactory(RegularUserFactory)

    account = factory.LazyAttribute(
        lambda o: o.initial_account if o.initial_account else factory.SubFactory(RegularUserFactory)
    )
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
    summary = "models.CharField(max_length=255, default="")"
    note = "Invoice note here"


class FinanceInvoiceItemFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.FinanceInvoiceItem

    # finance_invoice = factory.SubFactory(FinanceInvoiceFactory)
    class Params:
        initial_invoice = factory.SubFactory(FinanceInvoiceFactory)

    finance_invoice = factory.LazyAttribute(
        lambda o: o.initial_invoice if o.initial_invoice else factory.SubFactory(FinanceInvoiceFactory)
    )
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
    finance_invoice_group = factory.SubFactory(FinanceInvoiceGroupFactory)
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
    frequency_interval = 1 # Monday
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
    account_classpass = factory.SubFactory(AccountClasspassFactory)
    attendance_type = 'CLASSPASS'
    date = datetime.date(2030, 12, 30)
    online_booking = False
    booking_status = "ATTENDING"

    
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
