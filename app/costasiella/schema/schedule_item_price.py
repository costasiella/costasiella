from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import Account, ScheduleItem, ScheduleItemPrice, OrganizationClasspass
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()

class ScheduleItemPriceNode(DjangoObjectType):
    # Disable output like "A_3" by graphene automatically converting model choices
    # to an Enum field
    role = graphene.Field(graphene.String, source='role')
    role_2 = graphene.Field(graphene.String, source='role_2')

    class Meta:
        model = ScheduleItemPrice
        fields = (
            'schedule_item',
            'organization_classpass_dropin',
            'organization_classpass_trial',
            'date_start',
            'date_end',
            'created_at',
            'updated_at'
        )
        filter_fields = ['schedule_item']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_scheduleitemprice')

        # Return only public non-archived location rooms
        return self._meta.model.objects.get(id=id)


class ScheduleItemPriceQuery(graphene.ObjectType):
    schedule_item_prices = DjangoFilterConnectionField(ScheduleItemPriceNode)
    schedule_item_price = graphene.relay.Node.Field(ScheduleItemPriceNode)

    def resolve_schedule_item_prices(self, info, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_scheduleitemprice')

        return ScheduleItemPrice.objects.order_by('-date_start')
            

def validate_schedule_item_price_create_update_input(input):
    """
    Validate input
    """ 
    result = {}

    # Check Account
    if 'account' in input:
        if input['account']:
            rid = get_rid(input['account'])
            account = Account.objects.filter(id=rid.id).first()
            result['account'] = account
            if not account:
                raise Exception(_('Invalid Account ID!'))            

    # Check Account
    if 'account_2' in input:
        if input['account_2']:
            rid = get_rid(input['account_2'])
            account_2 = Account.objects.filter(id=rid.id).first()
            result['account_2'] = account_2
            if not account_2:
                raise Exception(_('Invalid Account ID!'))            

    # Check Schedule item
    if 'schedule_item' in input:
        if input['schedule_item']:
            rid = get_rid(input['schedule_item'])
            schedule_item = ScheduleItem.objects.get(id=rid.id)
            result['schedule_item'] = schedule_item
            if not schedule_item:
                raise Exception(_('Invalid Schedule Item (class) ID!'))   

    # Check Organization Classpass Dropin
    if 'organization_classpass_dropin' in input:
        result['organization_classpass_dropin'] = None
        if input['organization_classpass_dropin']:
            rid = get_rid(input['organization_classpass_dropin'])
            organization_classpass = OrganizationClasspass.objects.get(id=rid.id)
            result['organization_classpass_dropin'] = organization_classpass
            if not organization_classpass:
                raise Exception(_('Invalid Organization Classpass ID!'))   

    # Check Organization Classpass Trial
    if 'organization_classpass_trial' in input:
        result['organization_classpass_trial'] = None
        if input['organization_classpass_trial']:
            rid = get_rid(input['organization_classpass_trial'])
            organization_classpass = OrganizationClasspass.objects.get(id=rid.id)
            result['organization_classpass_trial'] = organization_classpass
            if not organization_classpass:
                raise Exception(_('Invalid Organization Classpass ID!'))


    return result


class CreateScheduleItemPrice(graphene.relay.ClientIDMutation):
    class Input:
        schedule_item = graphene.ID(required=True)
        organization_classpass_dropin = graphene.ID(required=True)
        organization_classpass_trial = graphene.ID(required=True)
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=False, default_value=None)

    schedule_item_price = graphene.Field(ScheduleItemPriceNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_scheduleitemprice')

        validation_result = validate_schedule_item_price_create_update_input(input)

        schedule_item_price = ScheduleItemPrice(
            schedule_item = validation_result['schedule_item'],
            date_start=input['date_start']
        )

        # Optional fields
        date_end = input.get('date_end', None)
        if date_end:
            schedule_item_price.date_end = date_end

        organization_classpass_dropin = validation_result.get('organization_classpass_dropin', None)
        if organization_classpass_dropin:
            schedule_item_price.organization_classpass_dropin = organization_classpass_dropin

        organization_classpass_trial = validation_result.get('organization_classpass_trial', None)
        if organization_classpass_trial:
            schedule_item_price.organization_classpass_trial = organization_classpass_trial

        schedule_item_price.save()

        return CreateScheduleItemPrice(schedule_item_price=schedule_item_price)


class UpdateScheduleItemPrice(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        organization_classpass_dropin = graphene.ID(required=False)
        organization_classpass_trial = graphene.ID(required=False)
        date_start = graphene.types.datetime.Date(required=False)
        date_end = graphene.types.datetime.Date(required=False)
        
    schedule_item_price = graphene.Field(ScheduleItemPriceNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_scheduleitemprice')

        rid = get_rid(input['id'])
        schedule_item_price = ScheduleItemPrice.objects.filter(id=rid.id).first()
        if not schedule_item_price:
            raise Exception('Invalid Schedule Item Instructor ID!')

        validation_result = validate_schedule_item_price_create_update_input(input)
        
        # Optional fields
        date_start = input.get('date_start', None)
        if date_start:
            schedule_item_price.date_start = date_start

        date_end = input.get('date_end', None)
        if date_end:
            schedule_item_price.date_end = date_end

        if 'organization_classpass_dropin' in validation_result:
            schedule_item_price.organization_classpass_dropin = \
                validation_result['organization_classpass_dropin']

        if 'organization_classpass_trial' in validation_result:
            schedule_item_price.organization_classpass_trial = \
                validation_result['organization_classpass_trial']

        schedule_item_price.save()

        return UpdateScheduleItemPrice(schedule_item_price=schedule_item_price)


class DeleteScheduleItemPrice(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_scheduleitemprice')

        rid = get_rid(input['id'])
        schedule_item_price = ScheduleItemPrice.objects.filter(id=rid.id).first()
        if not schedule_item_price:
            raise Exception('Invalid Schedule Item Price ID!')

        ok = bool(schedule_item_price.delete())

        return DeleteScheduleItemPrice(ok=ok)


class ScheduleItemPriceMutation(graphene.ObjectType):
    delete_schedule_item_price = DeleteScheduleItemPrice.Field()
    create_schedule_item_price = CreateScheduleItemPrice.Field()
    update_schedule_item_price = UpdateScheduleItemPrice.Field()
