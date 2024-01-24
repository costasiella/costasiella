from django.utils.translation import gettext as _
from django.db.models import Q
from django.utils import timezone

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import AccountAcceptedDocument, FinanceOrder, OrganizationClasspass, \
    OrganizationSubscription, \
    OrganizationDocument, \
    ScheduleEventTicket, \
    ScheduleItem, \
    SystemNotification
from ..models.choices.finance_order_statuses import get_finance_order_statuses
from ..modules.gql_tools import require_login, require_login_and_permission, get_rid, get_error_code
from ..modules.finance_tools import display_float_as_amount
from ..modules.messages import Messages

from ..dudes.mail_dude import MailDude

m = Messages()


class FinanceOrderInterface(graphene.Interface):
    id = graphene.GlobalID()
    order_number = graphene.Int()
    subtotal_display = graphene.String()
    tax_display = graphene.String()
    total_display = graphene.String()
    paid_display = graphene.String()
    balance_display = graphene.String()


class FinanceOrderNode(DjangoObjectType):
    class Meta:
        model = FinanceOrder
        fields = (
            'finance_invoice',
            'account',
            'status',
            'delivery_error_message',
            'message',
            'subtotal',
            'tax',
            'total',
            'created_at',
            'updated_at',
            # Reverse relations
            'items'
        )
        filter_fields = {
            'account': ['exact'],
            'status': ['exact'],
        }
        interfaces = (graphene.relay.Node, FinanceOrderInterface, )

    def resolve_order_number(self, info):
        return self.id

    def resolve_subtotal_display(self, info):
        return display_float_as_amount(self.subtotal)

    def resolve_tax_display(self, info):
        return display_float_as_amount(self.tax)

    def resolve_total_display(self, info):
        return display_float_as_amount(self.total)


    @classmethod
    def get_node(self, info, id):
        user = info.context.user

        finance_order = self._meta.model.objects.get(id=id)

        # Accounts can get details for their own orders
        if not finance_order.account.id == user.id:
            require_login_and_permission(user, 'costasiella.view_financeorder')

        return finance_order


class FinanceOrderQuery(graphene.ObjectType):
    finance_orders = DjangoFilterConnectionField(FinanceOrderNode)
    finance_order = graphene.relay.Node.Field(FinanceOrderNode)

    def resolve_finance_orders(self, info, archived=False, **kwargs):
        user = info.context.user
        require_login(user)

        view_permission = user.has_perm('costasiella.view_financeorder')

        if view_permission and 'account' in kwargs and kwargs['account']:
            # Allow user to filter by any account
            rid = get_rid(kwargs.get('account', user.id))
            account_id = rid.id
        elif view_permission:
            # return all
            account_id = None
        else:
            # A user can only query their own orders
            account_id = user.id

        order_by = '-pk'
        if account_id:
            return FinanceOrder.objects.filter(account=account_id).order_by(order_by)
        else:
            return FinanceOrder.objects.all().order_by(order_by)


def validate_create_update_input(input, user, update=False):
    """
    Validate input
    """ 
    result = {}

    # Fetch & check organization classpass
    if not update:
        # Create checks
        if 'schedule_event_ticket' in input:
            rid = get_rid(input["schedule_event_ticket"])
            schedule_event_ticket = ScheduleEventTicket.objects.get(id=rid.id)
            result['schedule_event_ticket'] = schedule_event_ticket
            if not schedule_event_ticket:
                raise Exception(_('Invalid Schedule Event Ticket ID!'))

            if schedule_event_ticket.is_sold_out():
                raise Exception(_("Unable to create order: This ticket has sold out."))

        if 'organization_classpass' in input:
            rid = get_rid(input["organization_classpass"])
            organization_classpass = OrganizationClasspass.objects.get(id=rid.id)
            result['organization_classpass'] = organization_classpass

            # Don't create the order in case the user has reached the trial pass limit
            if organization_classpass.trial_pass:
                if user.has_reached_trial_limit():
                    raise Exception(_("Unable to create order: Trial limit reached."))

            if not organization_classpass:
                raise Exception(_('Invalid Organization Classpass ID!'))

        if 'organization_subscription' in input:
            rid = get_rid(input["organization_subscription"])
            organization_subscription = OrganizationSubscription.objects.get(id=rid.id)
            result['organization_subscription'] = organization_subscription
            if not organization_subscription:
                raise Exception(_('Invalid Organization Subscription ID!'))

        if 'schedule_item' in input:
            if 'attendance_date' not in input:
                raise Exception(_('Date is required when specifying Schedule Item ID!'))
            rid = get_rid(input["schedule_item"])
            schedule_item = ScheduleItem.objects.get(id=rid.id)
            result['schedule_item'] = schedule_item
            if not schedule_item:
                raise Exception(_('Invalid Schedule Item ID!'))
    else:
        # Update checks
        order_statuses = get_finance_order_statuses()
        valid_statuses = [status[0] for status in order_statuses]
        if 'status' in input:
            if input['status'] in valid_statuses:
                result['status'] = input['status']
            else:
                raise Exception(_('Invalid Finance Order ID!'))

    return result


def create_finance_order_log_accepted_documents(info):
    """
    Log time when user accepted terms & privacy policy (if any)
    :param info: Execution env info
    :return: None
    """
    user = info.context.user
    x_forwarded_for = info.context.META.get('HTTP_X_FORWARDED_FOR', None)
    if x_forwarded_for:
        client_ip = x_forwarded_for.split(',')[0]
    else:
        client_ip = info.context.META.get('REMOTE_ADDR', "0.0.0.0")

    now = timezone.now()
    today = now.date()

    document_types = ['TERMS_AND_CONDITIONS', 'PRIVACY_POLICY']
    for document_type in document_types:
        documents = OrganizationDocument.objects.filter((
                Q(document_type=document_type) &
                Q(date_start__lte=today) &
                (Q(date_end__gte=today) | Q(date_end__isnull=True))
        ))

        for document in documents:
            accepted_document = AccountAcceptedDocument(
                account=user,
                document=document,
                client_ip=client_ip
            )
            accepted_document.save()


class CreateFinanceOrder(graphene.relay.ClientIDMutation):
    class Input:
        message = graphene.String(required=False, default_value="")
        schedule_event_ticket = graphene.ID(required=False)
        organization_classpass = graphene.ID(required=False)
        organization_subscription = graphene.ID(required=False)
        schedule_item = graphene.ID(required=False)
        attendance_date = graphene.types.datetime.Date(required=False)
        
    finance_order = graphene.Field(FinanceOrderNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login(user)

        validation_result = validate_create_update_input(input, user)
        finance_order = FinanceOrder(
            account=user,
            status="AWAITING_PAYMENT"
        )

        if 'message' in input:
            finance_order.message = input['message']

        # Save order
        finance_order.save()

        attendance_date = input.get('attendance_date', None)
        # Process items
        if 'schedule_event_ticket' in validation_result:
            finance_order.item_add_schedule_event_ticket(
                validation_result['schedule_event_ticket']
            )

        if 'organization_classpass' in validation_result:
            finance_order.item_add_classpass(validation_result['organization_classpass'],
                                             schedule_item=validation_result.get('schedule_item', None),
                                             attendance_date=attendance_date)

        if 'organization_subscription' in validation_result:
            finance_order.item_add_subscription(validation_result['organization_subscription'])

        # Accept terms and privacy policy
        create_finance_order_log_accepted_documents(info)

        # Deliver order in case it's free, no need for a payment
        if finance_order.total == 0:
            finance_order.deliver()

        # Notify user of receiving order
        mail_dude = MailDude(account=user,
                             email_template="order_received",
                             finance_order=finance_order)
        mail_dude.send()

        # Notify accounts to be notified
        system_notification = SystemNotification.objects.filter(
            name="order_received"
        ).first()
        for account in system_notification.accounts.all():
            mail_dude = MailDude(account=account,
                                 email_template="notification_order_received",
                                 finance_order=finance_order)
            mail_dude.send()

        return CreateFinanceOrder(finance_order=finance_order)


class UpdateFinanceOrder(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        status = graphene.String(required=False)

    finance_order = graphene.Field(FinanceOrderNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login(user)

        rid = get_rid(input['id'])
        finance_order = FinanceOrder.objects.filter(id=rid.id).first()
        if not finance_order:
            raise Exception('Invalid Finance Order ID!')

        validation_result = validate_create_update_input(input, None, update=True)

        # To change an order, permissions or ownership is required.
        if not user.has_perm('costasiella.change_financeorder'):
            if not finance_order.account.id == user.id:
                raise GraphQLError(m.user_permission_denied,
                                   extensions={'code': get_error_code('USER_PERMISSION_DENIED')})
            else:
                # User wants to change own order, check if status change is permitted.
                # Status can only be "Cancelled"
                if not validation_result.get('status', '') == "CANCELLED":
                    raise GraphQLError(m.user_invalid_order_status,
                                       extensions={'code': 'USER_INVALID_ORDER_STATUS'})

        if 'status' in validation_result:
            # Deliver order when current status isn't "delivered"
            if validation_result['status'] == 'DELIVERED' and finance_order.status != "DELIVERED":
                finance_order.deliver() # This will also set the status to 'DELIVERED'
            else:
                finance_order.status = validation_result['status']

        finance_order.save()

        return UpdateFinanceOrder(finance_order=finance_order)


class DeleteFinanceOrder(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()
    
    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_financeorder')

        rid = get_rid(input['id'])

        finance_order = FinanceOrder.objects.filter(id=rid.id).first()
        if not finance_order:
            raise Exception('Invalid Finance Order ID!')

        ok = bool(finance_order.delete())

        return DeleteFinanceOrder(ok=ok)


class FinanceOrderMutation(graphene.ObjectType):
    delete_finance_order = DeleteFinanceOrder.Field()
    create_finance_order = CreateFinanceOrder.Field()
    update_finance_order = UpdateFinanceOrder.Field()