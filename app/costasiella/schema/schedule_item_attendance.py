from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import Account, AccountClasspass, AccountSubscription, FinanceInvoiceItem, ScheduleItem, ScheduleItemAttendance
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

from ..dudes import ClassCheckinDude, ClassScheduleDude

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
        account = graphene.ID(required=True)
        schedule_item = graphene.ID(required=True)
        account_classpass = graphene.ID(required=False)
        account_subscription = graphene.ID(required=False)
        finance_invoice_item = graphene.ID(required=False)
        attendance_type = graphene.String(required=True)
        date = graphene.types.datetime.Date(required=True)
        online_booking = graphene.Boolean(required=False, default_value=False)
        booking_status = graphene.String(required=False, default_value="BOOKED")

    schedule_item_attendance = graphene.Field(ScheduleItemAttendanceNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_scheduleitemattendance')

        validation_result = validate_schedule_item_attendance_create_update_input(input)
        class_checkin_dude = ClassCheckinDude()
        class_schedule_dude = ClassScheduleDude()

        class_schedule_dude.schedule_item_takes_place_on_day(
            schedule_item = validation_result['schedule_item'],
            date = input['date']
        )
        
        if attendance_type == "CLASSPASS":
            if not validation_result['account_classpass']:
                raise Exception(_('accountClasspass field is mandatory when doing a class pass check-in'))

            schedule_item_attendance = class_checkin_dude.class_checkin_classpass(
                account = validation_result['account'],
                account_classpass = validation_result['account_classpass'],
                schedule_item = validation_result['schedule_item'],
                date = input['date'],
                booking_status = booking_status,
                online_booking = online_booking,                    
            )

        return CreateScheduleItemAttendance(schedule_item_attendance=schedule_item_attendance)


class UpdateScheduleItemAttendance(graphene.relay.ClientIDMutation):
    class Input:
        attendance_type = graphene.String(required=False)
        booking_status = graphene.String(required=False, default_value="BOOKED")
        
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

        if 'attendance_input' in input:
            schedule_item_attendance.attendance_type = input['attendance_type']
        
        if 'booking_status' in input:
            schedule_item_attendance.booking_status = input['booking_status']

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
    