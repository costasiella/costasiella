from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import Account, ScheduleItem, ScheduleItemInstructorAvailable
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class ScheduleItemInstructorAvailableNode(DjangoObjectType):
    class Meta:
        model = ScheduleItemInstructorAvailable
        fields = (
            'schedule_item',
            'account',
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
        require_login_and_permission(user, 'costasiella.view_scheduleiteminstructoravailable')

        # Return only public non-archived location rooms
        return self._meta.model.objects.get(id=id)


class ScheduleItemInstructorAvailableQuery(graphene.ObjectType):
    schedule_item_instructor_availabless = DjangoFilterConnectionField(ScheduleItemInstructorAvailableNode)
    schedule_item_instructor_available = graphene.relay.Node.Field(ScheduleItemInstructorAvailableNode)

    def resolve_schedule_item_instructors(self, info, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_scheduleiteminstructoravailable')

        return ScheduleItemInstructorAvailable.objects.order_by('-date_start')
            

def validate_schedule_item_instructor_available_create_update_input(input):
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

    # Check OrganizationClasstype
    if 'schedule_item' in input:
        if input['schedule_item']:
            rid = get_rid(input['schedule_item'])
            schedule_item = ScheduleItem.objects.get(id=rid.id)
            result['schedule_item'] = schedule_item
            if not schedule_item:
                raise Exception(_('Invalid Schedule Item (class) ID!'))        


    return result


class CreateScheduleItemInstructorAvailable(graphene.relay.ClientIDMutation):
    class Input:
        schedule_item = graphene.ID(required=True)
        account = graphene.ID(required=True)
        role = graphene.String(required=False, default_value="")
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=False, default_value=None)

    schedule_item_instructor_available = graphene.Field(ScheduleItemInstructorAvailableNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_scheduleiteminstructoravailable')

        validation_result = validate_schedule_item_instructor_available_create_update_input(input)

        schedule_item_instructor_available = ScheduleItemInstructorAvailable(
            schedule_item = validation_result['schedule_item'],
            account=validation_result['account'],
            date_start=input['date_start']
        )

        # Optional fields
        date_end = input.get('date_end', None)
        if date_end:
            schedule_item_instructor_available.date_end = date_end

        schedule_item_instructor_available.save()

        return CreateScheduleItemInstructorAvailable(schedule_item_instructor_available=schedule_item_instructor_available)


class UpdateScheduleItemInstructorAvailable(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        account = graphene.ID(required=True)
        role = graphene.String(required=False, default_value="")
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=False, default_value=None)
        
    schedule_item_instructor_available = graphene.Field(ScheduleItemInstructorAvailableNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_scheduleiteminstructoravailable')

        rid = get_rid(input['id'])
        schedule_item_instructor_available = ScheduleItemInstructorAvailable.objects.filter(id=rid.id).first()
        if not schedule_item_instructor_available:
            raise Exception('Invalid Schedule Item Instructor Available ID!')

        validation_result = validate_schedule_item_instructor_available_create_update_input(input)

        schedule_item_instructor_available.account=validation_result['account']
        schedule_item_instructor_available.date_start=input['date_start']
        
        # Optional fields
        if 'date_end' in input:
            schedule_item_instructor_available.date_end = input['date_end']

        schedule_item_instructor_available.save()

        return UpdateScheduleItemInstructorAvailable(schedule_item_instructor_available=schedule_item_instructor_available)


class DeleteScheduleItemInstructorAvailable(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_scheduleiteminstructoravailable')

        rid = get_rid(input['id'])
        schedule_item_instructor_available = ScheduleItemInstructorAvailable.objects.filter(id=rid.id).first()
        if not schedule_item_instructor_available:
            raise Exception('Invalid Schedule Item Instructor Available ID!')

        ok = bool(schedule_item_instructor_available.delete())

        return DeleteScheduleItemInstructorAvailable(ok=ok)


class ScheduleItemInstructorAvailableMutation(graphene.ObjectType):
    delete_schedule_item_instructor_available = DeleteScheduleItemInstructorAvailable.Field()
    create_schedule_item_instructor_available = CreateScheduleItemInstructorAvailable.Field()
    update_schedule_item_instructor_available = UpdateScheduleItemInstructorAvailable.Field()
    