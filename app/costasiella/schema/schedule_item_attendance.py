from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import Account, AccountClasspass, AccountSubscription, FinanceInvoiceItem, ScheduleItem, ScheduleItemAttendance
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()

class ScheduleItemAttendanceNode(DjangoObjectType):
    # Disable output like "A_3" by graphene automatically converting model choices
    # to an Enum field
    attendance_type = graphene.Field(graphene.String, source='attendance_type')
    booking_status = graphene.Field(graphene.String, source='booking_status')

    class Meta:
        model = ScheduleItemAttendance
        filter_fields = ['schedule_item', 'account', 'date']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_scheduleitemattendance')

        # Return only public non-archived location rooms
        return self._meta.model.objects.get(id=id)


class ScheduleItemAttendanceQuery(graphene.ObjectType):
    schedule_item_attendances = DjangoFilterConnectionField(ScheduleItemAttendanceNode)
    schedule_item_attendance = graphene.relay.Node.Field(ScheduleItemAttendanceNode)

    def resolve_schedule_item_attendances(self, info, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_scheduleitemattendance')

        return ScheduleItemAttendance.objects.order_by('-date_start')
            

def validate_schedule_item_attendance_create_update_input(input):
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

    # Check AccountClasspass
    if 'account_classpass' in input:
        if input['account_classpass']:
            rid = get_rid(input['account_classpass'])
            account_classpass = AccountClasspass.objects.filter(id=rid.id).first()
            result['account_classpass'] = account_classpass
            if not account_classpass:
                raise Exception(_('Invalid Account Classpass ID!'))                      

    # Check AccountSubscription
    if 'account_subscription' in input:
        if input['account_subscription']:
            rid = get_rid(input['account_subscription'])
            account_subscription = AccountSubscription.objects.filter(id=rid.id).first()
            result['account_subscription'] = account_subscription
            if not account_subscription:
                raise Exception(_('Invalid Account Subscription ID!'))                      

    # Check FinanceInvoiceItem
    if 'account_invoice_item' in input:
        if input['account_invoice_item']:
            rid = get_rid(input['account_invoice_item'])
            account_invoice_item = AccountInvoiceIteam.objects.filter(id=rid.id).first()
            result['account_invoice_item'] = account_invoice_item
            if not account_invoice_item:
                raise Exception(_('Invalid Account Invoice Item ID!'))                      

    # Check Schedule Item
    if 'schedule_item' in input:
        if input['schedule_item']:
            rid = get_rid(input['schedule_item'])
            schedule_item = ScheduleItem.objects.get(id=rid.id)
            result['schedule_item'] = schedule_item
            if not schedule_item:
                raise Exception(_('Invalid Schedule Item (class) ID!'))        


    return result


class CreateScheduleItemAttendance(graphene.relay.ClientIDMutation):
    class Input:
        schedule_item = graphene.ID(required=True)
        account = graphene.ID(required=True)
        role = graphene.String(required=False, default_value="")
        account_2 = graphene.ID(required=False, defailt_value="")
        role_2 = graphene.String(required=False, default_value="")
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=False, default_value=None)

    schedule_item_attendance = graphene.Field(ScheduleItemAttendanceNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_scheduleitemattendance')

        validation_result = validate_schedule_item_attendance_create_update_input(input)

        schedule_item_attendance = ScheduleItemAttendance(
            schedule_item = validation_result['schedule_item'],
            account=validation_result['account'],
            date_start=input['date_start']
        )

        # Optional fields
        date_end = input.get('date_end', None)
        if date_end:
            schedule_item_attendance.date_end = date_end

        role = input.get('role', None)
        if role:
            schedule_item_attendance.role = role

        account_2 = validation_result.get('account_2', None)
        if account_2:
            schedule_item_attendance.account_2 = account_2

        role_2 = input.get('role_2', None)
        if role_2:
            schedule_item_attendance.role_2 = role_2

        schedule_item_attendance.save()

        return CreateScheduleItemAttendance(schedule_item_attendance=schedule_item_attendance)


class UpdateScheduleItemAttendance(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        account = graphene.ID(required=True)
        role = graphene.String(required=False, default_value="")
        account_2 = graphene.ID(required=False)
        role_2 = graphene.String(required=False, default_value="")
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=False, default_value=None)
        
    schedule_item_attendance = graphene.Field(ScheduleItemAttendanceNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_scheduleitemattendance')

        rid = get_rid(input['id'])
        schedule_item_attendance = ScheduleItemAttendance.objects.filter(id=rid.id).first()
        if not schedule_item_attendance:
            raise Exception('Invalid Schedule Item Attendance ID!')

        validation_result = validate_schedule_item_attendance_create_update_input(input)

        schedule_item_attendance.account=validation_result['account']
        schedule_item_attendance.date_start=input['date_start']
        
        # Optional fields
        if 'date_end' in input:
            schedule_item_attendance.date_end = input['date_end']

        if 'role' in input:
            schedule_item_attendance.role = input['role']

        if 'account_2' in validation_result:
            schedule_item_attendance.account_2 = validation_result['account_2']

        if 'role_2' in input:
            schedule_item_attendance.role_2 = input['role_2']

        schedule_item_attendance.save()

        return UpdateScheduleItemAttendance(schedule_item_attendance=schedule_item_attendance)


class DeleteScheduleItemAttendance(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_scheduleitemattendance')

        rid = get_rid(input['id'])
        schedule_item_attendance = ScheduleItemAttendance.objects.filter(id=rid.id).first()
        if not schedule_item_attendance:
            raise Exception('Invalid Schedule Item Attendance ID!')

        ok = schedule_item_attendance.delete()

        return DeleteScheduleItemAttendance(ok=ok)


class ScheduleItemAttendanceMutation(graphene.ObjectType):
    delete_schedule_item_attendance = DeleteScheduleItemAttendance.Field()
    create_schedule_item_attendance = CreateScheduleItemAttendance.Field()
    update_schedule_item_attendance = UpdateScheduleItemAttendance.Field()
    