import factory

from .. import models
from django.contrib.auth import get_user_model


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
    credits_validity = 1
    reconciliation_classes = 1
    registration_fee = 20
    unlimited = False
    organization_membership = factory.SubFactory(OrganizationMembershipFactory)
    quick_stats_amount = 12.5
    finance_glaccount = factory.SubFactory(FinanceGLAccountFactory)
    finance_costcenter = factory.SubFactory(FinanceCostCenterFactory)


class OrganizationClasspassGroupFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OrganizationClasspassGroup

    archived = False
    name = "First class pass"


class OrganizationClasspassGroupClasspassFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OrganizationClasspassGroupClasspass

    organization_classpass_group = factory.SubFactory(OrganizationClasspassGroupFactory)
    organization_classpass = factory.SubFactory(OrganizationClasspassFactory)


class AdminFactory(factory.DjangoModelFactory):
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
    username = 'user'
    first_name = 'user'
    last_name = 'regular user'
    password = factory.PostGenerationMethodCall('set_password', 'CSUser!1#')

    is_active = True
