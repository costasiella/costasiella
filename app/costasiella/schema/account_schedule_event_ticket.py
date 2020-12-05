from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import Account, AccountScheduleEventTicket, ScheduleEventTicket
from ..modules.model_helpers.schedule_event_ticket_schedule_item_helper import ScheduleEventTicketScheduleItemHelper
from ..modules.gql_tools import require_login, require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class AccountScheduleEventTicketNode(DjangoObjectType):
    class Meta:
        model = AccountScheduleEventTicket
        filter_fields = ['account', 'schedule_event_ticket']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_accountscheduleeventticket')

        return self._meta.model.objects.get(id=id)


class AccountScheduleEventTicketQuery(graphene.ObjectType):
    account_schedule_event_tickets = DjangoFilterConnectionField(AccountScheduleEventTicketNode)
    account_schedule_event_ticket = graphene.relay.Node.Field(AccountScheduleEventTicketNode)

    def resolve_account_schedule_event_tickets(self, info, **kwargs):
        user = info.context.user
        # TODO: add permissions for users to view their own tickets.
        require_login_and_permission(user, 'costasiella.view_accountscheduleeventticket')
        # Has permission: check params

        if not "schedule_event_ticket" in kwargs and not "account" in kwargs:
            raise Exception(_("schedule_event_ticket or account is a required parameter"))

        if "schedule_event_ticket" in kwargs:
            rid = get_rid(kwargs["schedule_event_ticket"])
            return AccountScheduleEventTicket.objects.filter(
                schedule_event_ticket=rid.id
            ).order_by('account__full_name')

        if "account" in kwargs:
            rid = get_rid(kwargs["schedule_event_ticket"])
            return AccountScheduleEventTicket.objects.filter(
                account=rid.id
            ).order_by('schedule_event_ticket__schedule_event__date_start')


def validate_create_update_input(input, update=False):
    """
    Validate input
    """
    result = {}

    if not update:
        # Fetch & check schedule event ticket (insert only)
        rid = get_rid(input['account'])
        account = Account.objects.filter(id=rid.id).first()
        result['account'] = account
        if not account:
            raise Exception(_('Invalid Account ID!'))

        # Fetch & check schedule event ticket (insert only)
        rid = get_rid(input['schedule_event_ticket'])
        schedule_event_ticket = ScheduleEventTicket.objects.filter(id=rid.id).first()
        result['schedule_event_ticket'] = schedule_event_ticket
        if not schedule_event_ticket:
            raise Exception(_('Invalid Schedule Event Ticket ID!'))

    return result


class CreateAccountScheduleEventTicket(graphene.relay.ClientIDMutation):
    class Input:
        account = graphene.ID(required=True)
        schedule_event_ticket = graphene.ID(required=True)
        cancelled = graphene.Boolean(required=False)
        payment_confirmation = graphene.Boolean(required=False)
        info_mail_sent = graphene.Boolean(required=False)

    account_schedule_event_ticket = graphene.Field(AccountScheduleEventTicketNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_accountscheduleeventticket')

        # Validate input
        result = validate_create_update_input(input, update=False)

        account_schedule_event_ticket = AccountScheduleEventTicket(
            account=result['account'],
            schedule_event_ticket=result['schedule_event_ticket'],
        )

        if 'cancelled' in result:
            account_schedule_event_ticket.cancelled = result['cancelled']

        if 'payment_confirmation' in result:
            account_schedule_event_ticket.payment_confirmation = result['payment_confirmation']

        if 'info_mail_sent' in result:
            account_schedule_event_ticket.info_mail_sent = result['info_mail_sent']

        account_schedule_event_ticket.save()

        #TODO: use a dude to sell a ticket and use the dude to create an invoice

        return CreateAccountScheduleEventTicket(account_schedule_event_ticket=account_schedule_event_ticket)


class UpdateAccountScheduleEventTicket(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        cancelled = graphene.Boolean(required=False)
        payment_confirmation = graphene.Boolean(required=False)
        info_mail_sent = graphene.Boolean(required=False)
        
    account_schedule_event_ticket = graphene.Field(AccountScheduleEventTicketNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_accountscheduleeventticket')

        rid = get_rid(input['id'])
        account_schedule_event_ticket = AccountScheduleEventTicket.objects.filter(id=rid.id).first()
        if not account_schedule_event_ticket:
            raise Exception('Invalid Account Schedule Event Ticket ID!')

        # Validate input
        result = validate_create_update_input(input, update=True)

        if 'cancelled' in input:
            account_schedule_event_ticket.cancelled = input['cancelled']

        if 'payment_confirmation' in input:
            account_schedule_event_ticket.payment_confirmation = input['payment_confirmation']

        if 'info_mail_sent' in input:
            account_schedule_event_ticket.info_mail_sent = input['info_mail_sent']

        account_schedule_event_ticket.save()

        return UpdateAccountScheduleEventTicket(account_schedule_event_ticket=account_schedule_event_ticket)


class DeleteAccountScheduleEventTicket(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_accountscheduleeventticket')

        rid = get_rid(input['id'])
        account_schedule_event_ticket = AccountScheduleEventTicket.objects.filter(id=rid.id).first()
        if not account_schedule_event_ticket:
            raise Exception('Invalid Account Schedule Event Ticket ID!')

        ok = account_schedule_event_ticket.delete()

        return DeleteAccountScheduleEventTicket(ok=ok)


class AccountScheduleEventTicketMutation(graphene.ObjectType):
    delete_account_schedule_event_ticket = DeleteAccountScheduleEventTicket.Field()
    create_account_schedule_event_ticket = CreateAccountScheduleEventTicket.Field()
    update_account_schedule_event_ticket = UpdateAccountScheduleEventTicket.Field()
