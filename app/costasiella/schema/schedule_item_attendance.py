from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import Account, AccountClasspass, AccountSubscription, FinanceInvoiceItem, OrganizationClasspass, ScheduleItem, ScheduleItemAttendance
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

        return ScheduleItemAttendance.objects.order_by('-account__full_name')
            

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

    # Check OrganizationClasspass
    if 'organization_classpass' in input:
        if input['organization_classpass']:
            rid = get_rid(input['organization_classpass'])
            organization_classpass = OrganizationClasspass.objects.filter(id=rid.id).first()
            result['organization_classpass'] = organization_classpass
            if not organization_classpass:
                raise Exception(_('Invalid Organization Classpass ID!'))                      

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
        organization_classpass = graphene.ID(required=False)
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

        class_takes_place = class_schedule_dude.schedule_item_takes_place_on_day(
            schedule_item = validation_result['schedule_item'],
            date = input['date']
        )
        
        if not class_takes_place:
            raise Exception(_("This class doesn't take place on this date, please check for the correct date or any holidays."))
        
        attendance_type = input['attendance_type']
        if attendance_type == "CLASSPASS":
            if not validation_result['account_classpass']:
                raise Exception(_('accountClasspass field is mandatory when doing a class pass check-in'))

            account_classpass = validation_result['account_classpass']
            schedule_item_attendance = class_checkin_dude.class_checkin_classpass(
                account = validation_result['account'],
                account_classpass = account_classpass,
                schedule_item = validation_result['schedule_item'],
                date = input['date'],
                booking_status = input['booking_status'],
                online_booking = input['online_booking'],                    
            )

            account_classpass.update_classes_remaining()

        elif attendance_type == "SUBSCRIPTION":
            if not validation_result['account_subscription']:
                raise Exception(_('accountSubscription field is mandatory when doing a subscription check-in'))

            account_subscription = validation_result['account_subscription']
            schedule_item_attendance = class_checkin_dude.class_checkin_subscription(
                account = validation_result['account'],
                account_subscription = account_subscription,
                schedule_item = validation_result['schedule_item'],
                date = input['date'],
                booking_status = input['booking_status'],
                online_booking = input['online_booking'],                    
            )

            #TODO: add code to update available credits for a subscription

        #TODO: Add CLASSPASS_BUY_AND_BOOK
        elif attendance_type == "CLASSPASS_BUY_AND_BOOK":
            if not validation_result['organization_classpass']:
                raise Exception(_('organizationClasspass field is mandatory when doing a classpass buy and check-in'))

            organization_classpass = validation_result['organization_classpass']
            result = class_checkin_dude.sell_classpass_and_class_checkin(
                account = validation_result['account'],
                organization_classpass = organization_classpass,
                schedule_item = validation_result['schedule_item'],
                date = input['date'],
                booking_status = input['booking_status'],
                online_booking = input['online_booking'],                    
            )

            schedule_item_attendance = result['schedule_item_attendance']
            account_classpass = result['account_classpass']

            account_classpass.update_classes_remaining()
        

        return CreateScheduleItemAttendance(schedule_item_attendance=schedule_item_attendance)


class UpdateScheduleItemAttendance(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
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
        
        if 'booking_status' in input:
            schedule_item_attendance.booking_status = input['booking_status']

        schedule_item_attendance.save()

        # Update classpass classes remaining
        if schedule_item_attendance.account_classpass:
             schedule_item_attendance.account_classpass.update_classes_remaining()

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

        # Get linked class pass if any
        account_classpass = None
        if schedule_item_attendance.account_classpass:
             account_classpass = schedule_item_attendance.account_classpass

        # Actually remove
        ok = schedule_item_attendance.delete()

        if account_classpass:
            account_classpass.update_classes_remaining()

        return DeleteScheduleItemAttendance(ok=ok)


class ScheduleItemAttendanceMutation(graphene.ObjectType):
    delete_schedule_item_attendance = DeleteScheduleItemAttendance.Field()
    create_schedule_item_attendance = CreateScheduleItemAttendance.Field()
    update_schedule_item_attendance = UpdateScheduleItemAttendance.Field()
    