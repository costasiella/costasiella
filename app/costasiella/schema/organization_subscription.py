from django.utils.translation import gettext as _
from django.utils import timezone
from django.db.models import Q

import graphene
from decimal import Decimal

from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from graphql_relay import to_global_id

import datetime
import validators

from ..dudes import DateToolsDude, SystemSettingDude
from ..models import OrganizationSubscription, OrganizationMembership, FinanceCostCenter, FinanceGLAccount, FinanceTaxRate
from ..modules.finance_tools import display_float_as_amount
from ..modules.gql_tools import require_login, require_login_and_permission, get_rid
from ..modules.messages import Messages
from ..modules.validity_tools import display_subscription_unit


m = Messages()


def validate_create_update_input(input, update=False):
    """
    Validate input
    """ 
    result = {}
    
    if not len(input['name']):
        raise GraphQLError(_('Name is required'))

    # Check GLAccount
    if 'finance_glaccount' in input:
        if input['finance_glaccount']: 
            rid = get_rid(input['finance_glaccount'])
            finance_glaccount= FinanceGLAccount.objects.filter(id=rid.id).first()
            result['finance_glaccount'] = finance_glaccount
            if not finance_glaccount:
                raise Exception(_('Invalid Finance GLAccount ID!'))

    # Check Costcenter
    if 'finance_costcenter' in input:
        if input['finance_costcenter']:
            rid = get_rid(input['finance_costcenter'])
            finance_costcenter= FinanceCostCenter.objects.filter(id=rid.id).first()
            result['finance_costcenter'] = finance_costcenter
            if not finance_costcenter:
                raise Exception(_('Invalid Finance Costcenter ID!'))

    return result


class OrganizationSubscriptionNodeInterface(graphene.Interface):
    id = graphene.GlobalID()
    subscription_unit_display = graphene.String()
    price_today = graphene.Decimal()
    price_today_display = graphene.String()
    price_first_month = graphene.Decimal()
    price_first_month_display = graphene.String()
    account_registration_fee = graphene.Decimal()
    account_registration_fee_display = graphene.String()
    shop_payment_method = graphene.String()
    url_shop = graphene.String()


class OrganizationSubscriptionNode(DjangoObjectType):   
    class Meta:
        model = OrganizationSubscription
        fields = (
            'archived',
            'display_public',
            'display_shop',
            'name',
            'description',
            'sort_order',
            'min_duration',
            'classes',
            'subscription_unit',
            'reconciliation_classes',
            'credit_validity',
            'unlimited',
            'terms_and_conditions',
            'registration_fee',
            'quick_stats_amount',
            'finance_glaccount',
            'finance_costcenter'
        )
        filter_fields = ['archived', 'display_shop', 'display_public']
        interfaces = (graphene.relay.Node, OrganizationSubscriptionNodeInterface)

    def resolve_subscription_unit_display(self, info):
        return display_subscription_unit(self.subscription_unit)

    def resolve_price_today_display(self, info):
        today = timezone.now().date()

        return self.get_price_on_date(today, display=True)

    def resolve_price_today(self, info):
        today = timezone.now().date()

        return self.get_price_on_date(today)

    def resolve_price_first_month(self, info):
        today = timezone.now().date()

        return self.get_price_first_month(today)

    def resolve_price_first_month_display(self, info):
        today = timezone.now().date()

        return self.get_price_first_month(today, display=True)

    def resolve_account_registration_fee(self, info):
        if not info.context.user:
            return None

        account = info.context.user
        return self.get_account_registration_fee(account)

    def resolve_account_registration_fee_display(self, info):
        if not info.context.user:
            return None

        account = info.context.user
        return display_float_as_amount(self.get_account_registration_fee(account))

    def resolve_shop_payment_method(self, info):
        setting_dude = SystemSettingDude()
        payment_method = setting_dude.get('workflow_shop_subscription_payment_method')
        if not payment_method:
            payment_method = 'MOLLIE'

        return payment_method

    def resolve_url_shop(self, info):
        try:
            scheme = info.context.scheme
            host = info.context.get_host()
            global_event_id = to_global_id("OrganizationSubscriptionNode", self.id)

            url_shop = f"{scheme}://{host}/#/shop/subscription/{global_event_id}"
        except AttributeError:
            # Eg. When calling from another part piece of code instead of the API, info.context won't be available
            url_shop = ""

        return url_shop

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login(user)

        # Return only public non-archived subscriptions without a further permission check
        organization_subscription = self._meta.model.objects.get(id=id)
        user_has_subscription = user.subscriptions.filter(organization_subscription=organization_subscription).exists()

        if user_has_subscription or info.path.typename == "AccountSubscriptionNode":
            # Users can get info about subscriptions they have
            return organization_subscription
        elif (not organization_subscription.display_public and not organization_subscription.display_shop) or \
                organization_subscription.archived:
            # But for all other archived or non-public ones, they need permissions
            require_login_and_permission(user, 'costasiella.view_organizationsubscription')

        # Return if user has permission, or it's public and not archived.
        return organization_subscription


class OrganizationSubscriptionQuery(graphene.ObjectType):
    organization_subscriptions = DjangoFilterConnectionField(OrganizationSubscriptionNode)
    organization_subscription = graphene.relay.Node.Field(OrganizationSubscriptionNode)

    def resolve_organization_subscriptions(self, info, archived, **kwargs):
        user = info.context.user
        # Has permission: return everything the user asked for
        if user.has_perm('costasiella.view_organizationsubscription'):
            return OrganizationSubscription.objects.filter(archived=archived).order_by('name')

        # Return only public non-archived subscriptions
        return OrganizationSubscription.objects.filter(
            Q(display_public=True) | Q(display_shop=True)
        ).filter(archived=False).order_by('name')


class CreateOrganizationSubscription(graphene.relay.ClientIDMutation):
    class Input:
        display_public = graphene.Boolean(required=True, default_value=True)
        display_shop = graphene.Boolean(required=True, default_value=True)
        name = graphene.String(required=True)
        description = graphene.String(required=False, default_value="")
        sort_order = graphene.Int(required=True, default_value=0)
        min_duration = graphene.Int(required=True, default_value=1)
        classes = graphene.Int(required=True, default_value=1)
        subscription_unit = graphene.String(required=True)
        reconciliation_classes = graphene.Int(required=False, default_value=0)
        credit_validity = graphene.Int(required=False, default_value=0)
        unlimited = graphene.Boolean(required=True, default_value=False)
        terms_and_conditions = graphene.String(required=False, default_value="")
        registration_fee = graphene.Decimal(required=False, default_value=Decimal(0))
        quick_stats_amount = graphene.Decimal(required=False, default_value=Decimal(0))
        finance_glaccount = graphene.ID(required=False, default_value="")
        finance_costcenter = graphene.ID(required=False, default_value="")      

    organization_subscription = graphene.Field(OrganizationSubscriptionNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_organizationsubscription')

        # Validate input
        result = validate_create_update_input(input, update=False)

        subscription = OrganizationSubscription(
            display_public=input['display_public'],
            display_shop=input['display_shop'],
            name=input['name'], 
            description=input['description'],
            sort_order=input['sort_order'],
            min_duration=input['min_duration'],
            classes=input['classes'],
            subscription_unit=input['subscription_unit'],
            reconciliation_classes=input['reconciliation_classes'],
            credit_validity=input['credit_validity'],
            unlimited=input['unlimited'],
            terms_and_conditions=input['terms_and_conditions'],
            registration_fee=input['registration_fee'],
            quick_stats_amount=input.get('quick_stats_amount', None)
        )

        if 'finance_glaccount' in result:
            subscription.finance_glaccount = result['finance_glaccount']

        if 'finance_costcenter' in result:
            subscription.finance_costcenter = result['finance_costcenter']

        subscription.save()

        return CreateOrganizationSubscription(organization_subscription = subscription)


class UpdateOrganizationSubscription(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        display_public = graphene.Boolean(required=False)
        display_shop = graphene.Boolean(required=False)
        name = graphene.String(required=False)
        description = graphene.String(required=False)
        sort_order = graphene.Int(required=False)
        min_duration = graphene.Int(required=False)
        classes = graphene.Int(required=False)
        subscription_unit = graphene.String(required=False)
        reconciliation_classes = graphene.Int(required=False)
        credit_validity = graphene.Int(required=False)
        unlimited = graphene.Boolean(required=False)
        terms_and_conditions = graphene.String(required=False)
        registration_fee = graphene.Decimal(required=False)
        quick_stats_amount = graphene.Decimal(required=False)
        finance_glaccount = graphene.ID(required=False)
        finance_costcenter = graphene.ID(required=False)

    organization_subscription = graphene.Field(OrganizationSubscriptionNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_organizationsubscription')
    
        rid = get_rid(input['id'])
        subscription = OrganizationSubscription.objects.filter(id=rid.id).first()
        if not subscription:
            raise Exception('Invalid Organization Class pass ID!')

        result = validate_create_update_input(input, update=True)

        if 'display_public' in input:
            subscription.display_public = input['display_public']

        if 'display_shop' in input:
            subscription.display_shop = input['display_shop']

        if 'name' in input:
            subscription.name = input['name']

        if 'description' in input:
            subscription.description = input['description']

        if 'sort_order' in input:
            subscription.sort_order = input['sort_order']

        if 'min_duration' in input:
            subscription.min_duration = input['min_duration']

        if 'classes' in input:
            subscription.classes = input['classes']

        if 'subscription_unit' in input:
            subscription.subscription_unit = input['subscription_unit']

        if 'reconciliation_classes' in input:
            subscription.reconciliation_classes=input['reconciliation_classes']

        if 'credit_validity' in input:
            subscription.credit_validity = input['credit_validity']

        if 'unlimited' in input:
            subscription.unlimited = input['unlimited']

        if 'terms_and_conditions' in input:
            subscription.terms_and_conditions = input['terms_and_conditions']

        if 'registration_fee' in input:
            subscription.registration_fee = input['registration_fee']

        if 'quick_stats_amount' in input:
            subscription.quick_stats_amount = input['quick_stats_amount']

        if 'finance_glaccount' in result:
            subscription.finance_glaccount = result['finance_glaccount']

        if 'finance_costcenter' in result:
            subscription.finance_costcenter = result['finance_costcenter']

        subscription.save()

        return UpdateOrganizationSubscription(organization_subscription=subscription)


class ArchiveOrganizationSubscription(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    organization_subscription = graphene.Field(OrganizationSubscriptionNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_organizationsubscription')

        rid = get_rid(input['id'])
        subscription = OrganizationSubscription.objects.filter(id=rid.id).first()
        if not subscription:
            raise Exception('Invalid Organization Subscription ID!')

        subscription.archived = input['archived']
        subscription.save()

        return ArchiveOrganizationSubscription(organization_subscription=subscription)


class OrganizationSubscriptionMutation(graphene.ObjectType):
    archive_organization_subscription = ArchiveOrganizationSubscription.Field()
    create_organization_subscription = CreateOrganizationSubscription.Field()
    update_organization_subscription = UpdateOrganizationSubscription.Field()
