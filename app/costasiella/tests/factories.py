from django.utils import timezone
from django.contrib.auth import get_user_model

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


class AllAuthEmailAddress(factory.DjangoModelFactory):
    class Meta:
        model = EmailAddress

    user = factory.SubFactory(RegularUserFactory)
    email = 'user@costasiella.com'
    verified = True
    primary = True
    

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
    

class AccountMembershipFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.AccountMembership

    account = factory.SubFactory(RegularUserFactory)
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
    date_end = None
    note = "Subscription note here"
    

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
    
    
class ScheduleItemTeacherFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ScheduleItemTeacher

    schedule_item = factory.SubFactory(SchedulePublicWeeklyClassFactory)
    account = factory.SubFactory(TeacherFactory)
    account_2 = factory.SubFactory(Teacher2Factory)
    role_2 = "ASSISTANT"
    date_start = datetime.date(2014, 1, 1)
