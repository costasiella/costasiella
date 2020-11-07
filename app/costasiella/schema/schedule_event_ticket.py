from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import Account, ScheduleEvent, ScheduleEventTicket, FinanceTaxRate, FinanceGLAccount, FinanceCostCenter
from ..modules.gql_tools import require_login, require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()

class ScheduleEventTicketNodeInterface(graphene.Interface):
    id = graphene.GlobalID()
    price_display = graphene.String()


class ScheduleEventTicketNode(DjangoObjectType):
    class Meta:
        model = ScheduleEventTicket
        filter_fields = ['schedule_event']
        interfaces = (graphene.relay.Node, ScheduleEventTicketNodeInterface,)

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_scheduleevent')

        return self._meta.model.objects.get(id=id)

    def resolve_price_display(self, info):
        from ..modules.finance_tools import display_float_as_amount
        return display_float_as_amount(self.price)


class ScheduleEventTicketQuery(graphene.ObjectType):
    schedule_event_tickets = DjangoFilterConnectionField(ScheduleEventTicketNode)
    schedule_event_ticket = graphene.relay.Node.Field(ScheduleEventTicketNode)

    def resolve_schedule_event_tickets(self, info, schedule_event, **kwargs):
        user = info.context.user
        require_login(user)
        # Has permission: return everything requested
        if user.has_perm('costasiella.view_scheduleeventticket'):
            rid = get_rid(schedule_event)
            return ScheduleEventTicket.objects.filter(schedule_event=rid.id).order_by('-full_event', 'name')

        # Return only public non-archived locations
        return ScheduleEventTicket.objects.filter(display_public=True).order_by('-full_event', 'name')


def validate_create_update_input(input, update=False):
    """
    Validate input
    """
    result = {}

    if not update:
        # Fetch & check schedule event (insert only)
        rid = get_rid(input['schedule_event'])
        schedule_event = ScheduleEvent.objects.filter(id=rid.id).first()
        result['schedule_event'] = schedule_event
        if not schedule_event:
            raise Exception(_('Invalid Schedule Event ID!'))

    # Fetch & check tax rate
    if 'finance_tax_rate' in input:
        if input['finance_tax_rate']:
            rid = get_rid(input['finance_tax_rate'])
            finance_tax_rate = FinanceTaxRate.objects.filter(id=rid.id).first()
            result['finance_tax_rate'] = finance_tax_rate
            if not finance_tax_rate:
                raise Exception(_('Invalid Finance Tax Rate ID!'))

    # Check GLAccount
    if 'finance_glaccount' in input:
        if input['finance_glaccount']:
            rid = get_rid(input['finance_glaccount'])
            finance_glaccount = FinanceGLAccount.objects.filter(id=rid.id).first()
            result['finance_glaccount'] = finance_glaccount
            if not finance_glaccount:
                raise Exception(_('Invalid Finance GLAccount ID!'))

    # Check Costcenter
    if 'finance_costcenter' in input:
        if input['finance_costcenter']:
            rid = get_rid(input['finance_costcenter'])
            finance_costcenter = FinanceCostCenter.objects.filter(id=rid.id).first()
            result['finance_costcenter'] = finance_costcenter
            if not finance_costcenter:
                raise Exception(_('Invalid Finance Costcenter ID!'))

    return result


class CreateScheduleEventTicket(graphene.relay.ClientIDMutation):
    class Input:
        display_public = graphene.Boolean(required=False, default_value=True)
        schedule_event = graphene.ID(required=True)
        name = graphene.String(required=True)
        description = graphene.String(required=False, default_value="")
        price = graphene.Float(required=True, default_value=0)
        finance_tax_rate = graphene.ID(required=False)
        finance_glaccount = graphene.ID(required=False)
        finance_costcenter = graphene.ID(required=False)

    schedule_event_ticket = graphene.Field(ScheduleEventTicketNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_scheduleeventticket')

        # Validate input
        result = validate_create_update_input(input, update=False)

        schedule_event_ticket = ScheduleEventTicket(
            display_public=input['display_public'],
            schedule_event=result['schedule_event'],
            name=input['name'],
            description=input['description'],
            price=input['price']
        )

        if 'finance_tax_rate' in result:
            schedule_event_ticket.finance_tax_rate = result['finance_tax_rate']

        if 'finance_glaccount' in result:
            schedule_event_ticket.finance_glaccount = result['finance_glaccount']

        if 'finance_costcenter' in result:
            schedule_event_ticket.finance_costcenter = result['finance_costcenter']

        schedule_event_ticket.save()

        return CreateScheduleEventTicket(schedule_event_ticket=schedule_event_ticket)


class UpdateScheduleEventTicket(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        description = graphene.String(required=False, default_value="")
        price = graphene.Float(required=True, default_value=0)
        finance_tax_rate = graphene.ID(required=False)
        finance_glaccount = graphene.ID(required=False)
        finance_costcenter = graphene.ID(required=False)
        
    schedule_event_ticket = graphene.Field(ScheduleEventTicketNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_scheduleeventticket')

        rid = get_rid(input['id'])
        schedule_event_ticket = ScheduleEventTicket.objects.filter(id=rid.id).first()
        if not schedule_event_ticket:
            raise Exception('Invalid Schedule Event Ticket ID!')

        # Validate input
        result = validate_create_update_input(input, update=True)

        if 'display_public' in input:
            schedule_event_ticket.display_public = input['display_public']
        if 'name' in input:
            schedule_event_ticket.name = input['name']
        if 'description' in input:
            schedule_event_ticket.description = input['description']
        if 'price' in input:
            schedule_event_ticket.price = input['price']
        if 'finance_tax_rate' in result:
            schedule_event_ticket.finance_tax_rate = result['finance_tax_rate']
        if 'finance_glaccount' in result:
            schedule_event_ticket.finance_glaccount = result['finance_glaccount']
        if 'finance_costcenter' in result:
            schedule_event_ticket.finance_costcenter = result['finance_costcenter']

        schedule_event_ticket.save()

        return UpdateScheduleEventTicket(schedule_event_ticket=schedule_event_ticket)


class DeleteScheduleEventTicket(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_scheduleeventticket')

        rid = get_rid(input['id'])
        schedule_event_ticket = ScheduleEventTicket.objects.filter(id=rid.id).first()
        if not schedule_event_ticket:
            raise Exception('Invalid Schedule Event Ticket ID!')

        if not schedule_event_ticket.deletable or schedule_event_ticket.full_event:
            #  Don't delete the full event ticket; it should always be there.
            ok = False
        else:
            ok = schedule_event_ticket.delete()

        return DeleteScheduleEventTicket(ok=ok)


class ScheduleEventTicketMutation(graphene.ObjectType):
    delete_schedule_event_ticket = DeleteScheduleEventTicket.Field()
    create_schedule_event_ticket = CreateScheduleEventTicket.Field()
    update_schedule_event_ticket = UpdateScheduleEventTicket.Field()
