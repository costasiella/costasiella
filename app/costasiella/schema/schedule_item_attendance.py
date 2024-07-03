from django.utils.translation import gettext as _

import datetime
import pytz
import graphene
from django.utils import timezone
from django.conf import settings
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import Account, AccountClasspass, AccountSubscription, AccountSubscriptionCredit, \
                     FinanceInvoiceItem, OrganizationClasspass, ScheduleItem, ScheduleItemAttendance
from ..modules.gql_tools import require_login, require_login_and_permission, \
                                require_login_and_one_of_permissions, get_rid
from ..modules.messages import Messages
from ..modules.model_helpers.schedule_item_helper import ScheduleItemHelper

from ..dudes import ClassCheckinDude, ClassScheduleDude

m = Messages()


class ScheduleItemAttendanceNodeInterface(graphene.Interface):
    id = graphene.GlobalID()
    cancellation_until = graphene.types.datetime.DateTime()
    cancellation_possible = graphene.Boolean()
    uncancellation_possible = graphene.Boolean()


class ScheduleItemAttendanceNode(DjangoObjectType):
    # Disable output like "A_3" by graphene automatically converting model choices
    # to an Enum field
    attendance_type = graphene.Field(graphene.String, source='attendance_type')
    booking_status = graphene.Field(graphene.String, source='booking_status')

    class Meta:
        model = ScheduleItemAttendance
        fields = (
            'account',
            'schedule_item',
            'account_classpass',
            'account_subscription',
            'account_schedule_event_ticket',
            'finance_invoice_item',
            'attendance_type',
            'date',
            'online_booking',
            'booking_status',
            'created_at',
            'updated_at'
        )
        # account_schedule_event_ticket_Isnull filter can be used to differentiate class & event attendance
        filter_fields = {
            'schedule_item': ['exact', 'isnull'],
            'account': ['exact'],
            'date': ['exact'],
            'account_schedule_event_ticket': ['isnull']
        }
        interfaces = (graphene.relay.Node, ScheduleItemAttendanceNodeInterface)

    @classmethod
    def get_node(cls, info, id):
        user = info.context.user
        require_login(user)

        schedule_item_attendance = cls._meta.model.objects.get(id=id)
        # Accounts can view their own attendance
        if not schedule_item_attendance.account.id == user.id:
            require_login_and_one_of_permissions(user, [
                'costasiella.view_scheduleitemattendance',
                'costasiella.view_selfcheckin'
            ])

        return schedule_item_attendance

    def resolve_cancellation_until(self, info):
        """
            Calculates datetime of latest cancellation possibility
        """
        return self.get_cancel_before()
    
    def resolve_cancellation_possible(self, info):
        local_tz = pytz.timezone(settings.TIME_ZONE)

        now = timezone.localtime(timezone.now())
        cancel_before = self.get_cancel_before()

        if now < cancel_before and self.booking_status == 'BOOKED':
            return True
        else:
            return False

    def resolve_uncancellation_possible(self, info):
        from ..dudes import ClassCheckinDude

        uncancel_possible = True

        now = timezone.now()
        if now.date() > self.date:
            # It's not possible to book classes in the past
            uncancel_possible = False

        class_checkin_dude = ClassCheckinDude()
        class_is_full = class_checkin_dude.check_class_is_full(self.schedule_item, self.date)
        if class_is_full:
            uncancel_possible = False

        # Invert value, cancellation is only possible if the class isn't full
        return uncancel_possible


class ScheduleItemAttendanceQuery(graphene.ObjectType):
    schedule_item_attendances = DjangoFilterConnectionField(ScheduleItemAttendanceNode)
    schedule_item_attendance = graphene.relay.Node.Field(ScheduleItemAttendanceNode)

    def resolve_schedule_item_attendances(self, info, **kwargs):
        user = info.context.user
        require_login(user)

        view_permission = user.has_perm('costasiella.view_scheduleitemattendance') or \
            user.has_perm('costasiella.view_selfcheckin')

        if view_permission and 'account' in kwargs and kwargs['account']:
            # Allow user to filter by any account
            rid = get_rid(kwargs.get('account', user.id))
            account_id = rid.id
        elif view_permission:
            # return all
            account_id = None
        else:
            # A user can only query their own attendances
            account_id = user.id

        if account_id:
            order_by = '-date'
            return ScheduleItemAttendance.objects.filter(account=account_id).order_by(order_by)
        else:
            order_by = 'account__full_name'
            return ScheduleItemAttendance.objects.all().order_by(order_by)
            

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
    if 'finance_invoice_item' in input:
        if input['finance_invoice_item']:
            rid = get_rid(input['finance_invoice_item'])
            finance_invoice_item = FinanceInvoiceItem.objects.filter(id=rid.id).first()
            result['finance_invoice_item'] = finance_invoice_item
            if not finance_invoice_item:
                raise Exception(_('Invalid Finance Invoice Item ID!'))

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
        account = graphene.ID(required=False)
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
        require_login(user)

        permission = user.has_perm('costasiella.add_scheduleitemattendance') or \
            user.has_perm('costasiella.view_selfcheckin')

        validation_result = validate_schedule_item_attendance_create_update_input(input)
        if not permission or 'account' not in input:
            # When the user doesn't have permissions; always use their own account
            validation_result['account'] = user

        # Get the class OTC data if any for given date.
        sih = ScheduleItemHelper()
        schedule_item = sih.schedule_item_with_otc_and_holiday_data(
            validation_result['schedule_item'],
            input['date']
        )

        class_checkin_dude = ClassCheckinDude()
        class_schedule_dude = ClassScheduleDude()

        class_takes_place = class_schedule_dude.schedule_item_takes_place_on_day(
            schedule_item=schedule_item,
            date=input['date']
        )
        
        if not class_takes_place:
            raise Exception(
                _("This class doesn't take place on this date, please check for the correct date or any holidays.")
            )

        attendance_type = input['attendance_type']
        if attendance_type == "CLASSPASS":
            if not validation_result['account_classpass']:
                raise Exception(_('accountClasspass field is mandatory when doing a class pass check-in'))

            account_classpass = validation_result['account_classpass']
            schedule_item_attendance = class_checkin_dude.class_checkin_classpass(
                account=validation_result['account'],
                account_classpass=account_classpass,
                schedule_item=schedule_item,
                date=input['date'],
                booking_status=input['booking_status'],
                online_booking=input['online_booking'],
            )

            account_classpass.update_classes_remaining()

        elif attendance_type == "SUBSCRIPTION":
            if not validation_result['account_subscription']:
                raise Exception(_('accountSubscription field is mandatory when doing a subscription check-in'))

            account_subscription = validation_result['account_subscription']
            schedule_item_attendance = class_checkin_dude.class_checkin_subscription(
                account=validation_result['account'],
                account_subscription=account_subscription,
                schedule_item=schedule_item,
                date=input['date'],
                booking_status=input['booking_status'],
                online_booking=input['online_booking'],
            )

        elif attendance_type == "CLASSPASS_BUY_AND_BOOK":
            if not validation_result['organization_classpass']:
                raise Exception(_('organizationClasspass field is mandatory when doing a classpass buy and check-in'))

            organization_classpass = validation_result['organization_classpass']
            result = class_checkin_dude.sell_classpass_and_class_checkin(
                account=validation_result['account'],
                organization_classpass=organization_classpass,
                schedule_item=schedule_item,
                date=input['date'],
                booking_status=input['booking_status'],
                online_booking=input['online_booking'],
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
        require_login(user)

        rid = get_rid(input['id'])
        schedule_item_attendance = ScheduleItemAttendance.objects.filter(id=rid.id).first()
        if not schedule_item_attendance:
            raise Exception('Invalid Schedule Item Attendance ID!')

        # Accounts can modify the booking status of their own bookings
        if not schedule_item_attendance.account.id == user.id:
            require_login_and_one_of_permissions(user, [
                'costasiella.change_scheduleitemattendance',
                'costasiella.view_selfcheckin'
            ])

        validation_result = validate_schedule_item_attendance_create_update_input(input)
        
        if 'booking_status' in input:
            schedule_item_attendance.booking_status = input['booking_status']

        schedule_item_attendance.save()

        # Update classpass classes remaining
        if schedule_item_attendance.account_classpass:
             schedule_item_attendance.account_classpass.update_classes_remaining()

        # Update subscription credit status
        if schedule_item_attendance.account_subscription:
            # Refund subscription credit (Unlink schedule item attendance)
            if input['booking_status'] == 'CANCELLED':
                schedule_item_attendance.cancel()
                # account_subscription_credit = AccountSubscriptionCredit.objects.filter(
                #     schedule_item_attendance=schedule_item_attendance,
                # ).first()
                # account_subscription_credit.schedule_item_attendance = None
                # account_subscription_credit.save()

            # Link schedule item attendance to a credit, if not already linked
            if input['booking_status'] == 'BOOKED' or input['booking_status'] == 'ATTENDING':
                qs = AccountSubscriptionCredit.objects.filter(
                    schedule_item_attendance=schedule_item_attendance
                )
                if not qs.exists():
                    from ..dudes import ClassCheckinDude
                    class_checkin_dude = ClassCheckinDude()
                    class_checkin_dude.class_checkin_subscription_take_credit(schedule_item_attendance)

        return UpdateScheduleItemAttendance(schedule_item_attendance=schedule_item_attendance)


class DeleteScheduleItemAttendance(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_one_of_permissions(user, [
            'costasiella.delete_scheduleitemattendance',
            'costasiella.view_selfcheckin'
        ])

        rid = get_rid(input['id'])
        schedule_item_attendance = ScheduleItemAttendance.objects.filter(id=rid.id).first()
        if not schedule_item_attendance:
            raise Exception('Invalid Schedule Item Attendance ID!')

        # Get linked class pass if any
        account_classpass = None
        if schedule_item_attendance.account_classpass:
             account_classpass = schedule_item_attendance.account_classpass

        # Actually remove
        ok = bool(schedule_item_attendance.delete())

        if account_classpass:
            account_classpass.update_classes_remaining()

        return DeleteScheduleItemAttendance(ok=ok)


class ResendInfoMailScheduleItemAttendance(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_scheduleitemattendance')

        from ..dudes import ClassCheckinDude, ClassScheduleDude

        rid = get_rid(input['id'])
        schedule_item_attendance = ScheduleItemAttendance.objects.filter(id=rid.id).first()
        if not schedule_item_attendance:
            raise Exception('Invalid Schedule Item Attendance ID!')

        schedule_item = schedule_item_attendance.schedule_item
        account = schedule_item_attendance.account
        date = schedule_item_attendance.date

        class_schedule_dude = ClassScheduleDude()
        if not class_schedule_dude.schedule_item_takes_place_on_day(schedule_item, date):
            raise Exception("Class doesn't take place on this date!")

        class_checkin_dude = ClassCheckinDude()
        class_checkin_dude.send_info_mail(account, schedule_item, date)

        ok = True

        return ResendInfoMailScheduleItemAttendance(ok=ok)


class ScheduleItemAttendanceMutation(graphene.ObjectType):
    delete_schedule_item_attendance = DeleteScheduleItemAttendance.Field()
    create_schedule_item_attendance = CreateScheduleItemAttendance.Field()
    update_schedule_item_attendance = UpdateScheduleItemAttendance.Field()
    resend_info_mail_schedule_item_attendance = ResendInfoMailScheduleItemAttendance.Field()
