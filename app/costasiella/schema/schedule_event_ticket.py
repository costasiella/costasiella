from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import Account, ScheduleEvent, ScheduleEventTicket, FinanceTaxRate, FinanceGLAccount, FinanceCostCenter
from ..modules.gql_tools import require_login, require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class ScheduleEventTicketNode(DjangoObjectType):
    class Meta:
        model = ScheduleEventTicket
        filter_fields = ['schedule_event']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_scheduleevent')

        return self._meta.model.objects.get(id=id)


class ScheduleEventTicketQuery(graphene.ObjectType):
    schedule_event_tickets = DjangoFilterConnectionField(ScheduleEventTicketNode)
    schedule_event_ticket = graphene.relay.Node.Field(ScheduleEventTicketNode)

    def resolve_schedule_event_tickets(self, info, schedule_event, **kwargs):
        user = info.context.user
        require_login(user)
        # Has permission: return everything requested
        if user.has_perm('costasiella.view_scheduleeventticket'):
            return ScheduleEventTicket.objects.filter(schedule_event=schedule_event).order_by('-full_event', 'name')

        # Return only public non-archived locations
        return ScheduleEventTicket.objects.filter(display_public=True).order_by('-full_event', 'name')


def validate_create_update_input(input, update=False):
    """
    Validate input
    """
    result = {}

    # Fetch & check account
    # if not update:
    #     # Create only
    #     rid = get_rid(input['organization_location'])
    #     organization_location = OrganizationLocation.objects.filter(id=rid.id).first()
    #     result['organization_location'] = organization_location
    #     if not organization_location:
    #         raise Exception(_('Invalid Organization Location ID!'))

    # Fetch & check organization classpass
    # rid = get_rid(input['organization_classpass'])
    # organization_classpass = OrganizationClasspass.objects.get(pk=rid.id)
    # result['organization_classpass'] = organization_classpass
    # if not organization_classpass:
    #     raise Exception(_('Invalid Organization Classpass ID!'))

    if not update:
        # Fetch & check schedule event (insert only)
        rid = get_rid(input['schedule_event'])
        schedule_event = ScheduleEvent.objects.filter(id=rid.id).first()
        result['schedule_event'] = schedule_event
        if not schedule_event:
            raise Exception(_('Invalid Schedule Event ID!'))

    # Fetch & check tax rate
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

    # # Fetch & check organization level
    # if 'organization_level' in input:
    #     rid = get_rid(input['organization_level'])
    #     organization_level = OrganizationLevel.objects.filter(id=rid.id).first()
    #     result['organization_level'] = organization_level
    #     if not organization_level:
    #         raise Exception(_('Invalid Organization Level ID!'))
    #
    # # Fetch & check teacher (account)
    # if 'teacher' in input:
    #     rid = get_rid(input['teacher'])
    #     teacher = Account.objects.filter(id=rid.id).first()
    #     result['teacher'] = teacher
    #     if not teacher:
    #         raise Exception(_('Invalid Account ID (teacher)!'))
    #
    # # Fetch & check teacher_2 (account)
    # if 'teacher_2' in input:
    #     rid = get_rid(input['teacher_2'])
    #     teacher_2 = Account.objects.filter(id=rid.id).first()
    #     result['teacher_2'] = teacher_2
    #     if not teacher_2:
    #         raise Exception(_('Invalid Account ID (teacher2)!'))

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
        require_login_and_permission(user, 'costasiella.add_scheduleevent')

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


class UpdateScheduleEvent(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        display_public = graphene.Boolean(required=False)
        display_shop = graphene.Boolean(required=False)
        auto_send_info_mail = graphene.Boolean(required=False)
        organization_location = graphene.ID(required=False)
        organization_level = graphene.ID(required=False)
        name = graphene.String(required=False)
        tagline = graphene.String(required=False)
        preview = graphene.String(required=False)
        description = graphene.String(required=False)
        teacher = graphene.ID(required=False)
        teacher_2 = graphene.ID(required=False)
        info_mail_content = graphene.String(required=False)
        
    schedule_event = graphene.Field(ScheduleEventNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_scheduleevent')

        rid = get_rid(input['id'])
        schedule_event = ScheduleEvent.objects.filter(id=rid.id).first()
        if not schedule_event:
            raise Exception('Invalid Schedule Event ID!')

        # Validate input
        result = validate_create_update_input(input, update=True)

        if 'display_public' in input:
            schedule_event.display_public = input['display_public']
        if 'display_shop' in input:
            schedule_event.display_shop = input['display_shop']
        if 'auto_send_info_mail' in input:
            schedule_event.display_shop = input['auto_send_info_mail']
        if 'organization_location' in result:
            schedule_event.organization_location = result['organization_location']
        if 'organization_level' in result:
            schedule_event.organization_level = result['organization_level']
        if 'name' in input:
            schedule_event.name = input['name']
        if 'tagline' in input:
            schedule_event.tagline = input['tagline']
        if 'preview' in input:
            schedule_event.preview = input['preview']
        if 'description' in input:
            schedule_event.description = input['description']
        if 'teacher' in result:
            schedule_event.teacher = result['teacher']
        if 'teacher_2' in result:
            schedule_event.teacher_2 = result['teacher_2']
        if 'info_mail_content' in input:
            schedule_event.info_mail_content = input['info_mail_content']

        schedule_event.save()

        return UpdateScheduleEvent(schedule_event=schedule_event)


class ArchiveScheduleEvent(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    schedule_event = graphene.Field(ScheduleEventNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_scheduleevent')

        rid = get_rid(input['id'])
        schedule_event = ScheduleEvent.objects.filter(id=rid.id).first()
        if not schedule_event:
            raise Exception('Invalid Schedule Event ID!')

        schedule_event.archived = input['archived']
        schedule_event.save()

        return ArchiveScheduleEvent(schedule_event=schedule_event)


class ScheduleEventMutation(graphene.ObjectType):
    archive_schedule_event = ArchiveScheduleEvent.Field()
    create_schedule_event = CreateScheduleEvent.Field()
    update_schedule_event = UpdateScheduleEvent.Field()
