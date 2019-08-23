from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import Account, ScheduleItem, ScheduleItemTeacherAvailable
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()

class ScheduleItemTeacherAvailableNode(DjangoObjectType):
    class Meta:
        model = ScheduleItemTeacherAvailable
        filter_fields = ['schedule_item']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_scheduleitemteacheravailable')

        # Return only public non-archived location rooms
        return self._meta.model.objects.get(id=id)


class ScheduleItemTeacherAvailableQuery(graphene.ObjectType):
    schedule_item_teacher_availabless = DjangoFilterConnectionField(ScheduleItemTeacherAvailableNode)
    schedule_item_teacher_available = graphene.relay.Node.Field(ScheduleItemTeacherAvailableNode)

    def resolve_schedule_item_teachers(self, info, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_scheduleitemteacheravailable')

        return ScheduleItemTeacherAvailable.objects.order_by('-date_start')
            

def validate_schedule_item_teacher_available_create_update_input(input):
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


class CreateScheduleItemTeacherAvailable(graphene.relay.ClientIDMutation):
    class Input:
        schedule_item = graphene.ID(required=True)
        account = graphene.ID(required=True)
        role = graphene.String(required=False, default_value="")
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=False, default_value=None)

    schedule_item_teacher_available = graphene.Field(ScheduleItemTeacherAvailableNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_scheduleitemteacheravailable')

        validation_result = validate_schedule_item_teacher_available_create_update_input(input)

        schedule_item_teacher_available = ScheduleItemTeacherAvailable(
            schedule_item = validation_result['schedule_item'],
            account=validation_result['account'],
            date_start=input['date_start']
        )

        # Optional fields
        date_end = input.get('date_end', None)
        if date_end:
            schedule_item_teacher_available.date_end = date_end

        schedule_item_teacher_available.save()

        return CreateScheduleItemTeacherAvailable(schedule_item_teacher_available=schedule_item_teacher_available)


class UpdateScheduleItemTeacherAvailable(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        account = graphene.ID(required=True)
        role = graphene.String(required=False, default_value="")
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=False, default_value=None)
        
    schedule_item_teacher_available = graphene.Field(ScheduleItemTeacherAvailableNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_scheduleitemteacheravailable')

        rid = get_rid(input['id'])
        schedule_item_teacher_available = ScheduleItemTeacherAvailable.objects.filter(id=rid.id).first()
        if not schedule_item_teacher_available:
            raise Exception('Invalid Schedule Item Teacher Available ID!')

        validation_result = validate_schedule_item_teacher_available_create_update_input(input)

        schedule_item_teacher_available.account=validation_result['account']
        schedule_item_teacher_available.date_start=input['date_start']
        
        # Optional fields
        if 'date_end' in input:
            schedule_item_teacher_available.date_end = input['date_end']

        schedule_item_teacher_available.save()

        return UpdateScheduleItemTeacherAvailable(schedule_item_teacher_available=schedule_item_teacher_available)


class DeleteScheduleItemTeacherAvailable(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_scheduleitemteacheravailable')

        rid = get_rid(input['id'])
        schedule_item_teacher_available = ScheduleItemTeacherAvailable.objects.filter(id=rid.id).first()
        if not schedule_item_teacher_available:
            raise Exception('Invalid Schedule Item Teacher Available ID!')

        ok = schedule_item_teacher_available.delete()

        return DeleteScheduleItemTeacherAvailable(ok=ok)


class ScheduleItemTeacherAvailableMutation(graphene.ObjectType):
    delete_schedule_item_teacher_available = DeleteScheduleItemTeacherAvailable.Field()
    create_schedule_item_teacher_available = CreateScheduleItemTeacherAvailable.Field()
    update_schedule_item_teacher_available = UpdateScheduleItemTeacherAvailable.Field()
    