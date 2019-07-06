from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import Account, ScheduleItem, ScheduleItemTeacher
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()

class ScheduleItemTeacherNode(DjangoObjectType):
    # Disable output like "A_3" by graphene automatically converting model choices
    # to an Enum field
    role = graphene.Field(graphene.String, source='role')
    role_2 = graphene.Field(graphene.String, source='role+2')

    class Meta:
        model = ScheduleItemTeacher
        filter_fields = ['schedule_item']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_scheduleitemteacher')

        # Return only public non-archived location rooms
        return self._meta.model.objects.get(id=id)


class ScheduleItemTeacherQuery(graphene.ObjectType):
    schedule_item_teachers = DjangoFilterConnectionField(ScheduleItemTeacherNode)
    schedule_item_teacher = graphene.relay.Node.Field(ScheduleItemTeacherNode)

    def resolve_schedule_item_teachers(self, info, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_scheduleitemteacher')

        return ScheduleItemTeacher.objects.order_by('date_start')
            

def validate_schedule_item_teacher_create_update_input(input):
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

    # Check OrganizationClasstype
    if 'schedule_item' in input:
        if input['schedule_item']:
            rid = get_rid(input['schedule_item'])
            schedule_item = ScheduleItem.objects.get(id=rid.id)
            result['schedule_item'] = schedule_item
            if not schedule_item:
                raise Exception(_('Invalid Schedule Item (class) ID!'))        


    return result


class CreateScheduleItemTeacher(graphene.relay.ClientIDMutation):
    class Input:
        schedule_item = graphene.ID(required=True)
        account = graphene.ID(required=True)
        role = graphene.String(required=False, default_value="")
        account_2 = graphene.ID(required=False, defailt_value="")
        role_2 = graphene.String(required=False, default_value="")
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=False, default_value=None)

    schedule_item_teacher = graphene.Field(ScheduleItemTeacherNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_scheduleitemteacher')
        validation_result = validate_schedule_item_teacher_create_update_input(input)

        schedule_item_teacher = ScheduleItemTeacher(
            schedule_item = validation_result['schedule_item'],
            account=validation_result['account'],
            date_start=input['date_start']
        )

        # Optional fields
        date_end = input.get('date_end', None)
        if date_end:
            schedule_item_teacher.date_end = date_end

        role = input.get('role', None)
        if role:
            schedule_item_teacher.role = role

        account_2 = validation_result.get('account_2', None)
        if account_2:
            schedule_item_teacher.account_2 = account_2

        role_2 = input.get('role_2', None)
        if role_2:
            schedule_item_teaher.role_2 = role_2

        schedule_item_teacher.save()

        return CreateScheduleItemTeacher(schedule_item_teacher=schedule_item_teacher)


class UpdateScheduleItemTeacher(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        schedule_item = graphene.ID(required=True)
        account = graphene.ID(required=True)
        role = graphene.String(required=False, default_value="")
        account_2 = graphene.ID(required=True)
        role_2 = graphene.String(required=False, default_value="")
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=False, default_value=None)
        
    schedule_item_teacher = graphene.Field(ScheduleItemTeacherNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_scheduleitemteacher')

        rid = get_rid(input['id'])
        schedule_item_teacher = ScheduleItemTeacher.objects.filter(id=rid.id).first()
        if not schedule_item_teacher:
            raise Exception('Invalid Schedule Item Teacher ID!')

        validation_result = validate_schedule_item_teacher_create_update_input(input)

        schedule_item_teacher.schedule_item = validation_result['schedule_item']
        schedule_item_teacher.account=validation_result['account']
        schedule_item_teacher.date_start=input['date_start']
        
        # Optional fields
        date_end = input.get('date_end', None)
        if date_end:
            schedule_item_teacher.date_end = date_end

        role = input.get('role', None)
        if role:
            schedule_item_teacher.role = role

        account_2 = validation_result.get('account_2', None)
        if account_2:
            schedule_item_teacher.account_2 = account_2

        role_2 = input.get('role_2', None)
        if role_2:
            schedule_item_teacher.role_2 = role_2

        schedule_item_teacher.save()

        return UpdateScheduleItemTeacher(schedule_item_teacher=schedule_item_teacher)


class DeleteScheduleItemTeacher(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_scheduleitemteacher')

        rid = get_rid(input['id'])
        schedule_item_teacher = ScheduleItemTeacher.objects.filter(id=rid.id).first()
        if not schedule_item_teacher:
            raise Exception('Invalid Schedule Item Teacher ID!')

        ok = schedule_item_teacher.delete()

        return DeleteScheduleItemTeacher(ok=ok)


class ScheduleItemTeacherMutation(graphene.ObjectType):
    delete_schedule_item_teacher = DeleteScheduleItemTeacher.Field()
    create_schedule_item_teacher = CreateScheduleItemTeacher.Field()
    update_schedule_item_teacher = UpdateScheduleItemTeacher.Field()
    