from django.utils.translation import gettext as _

import datetime
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import OrganizationAppointment, OrganizationAppointmentPrice, FinanceTaxRate
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.date_tools import last_day_month
from ..modules.messages import Messages

m = Messages()


def validate_create_update_input(input, update=False):
    """
    Validate input
    """ 
    result = {}

    # Fetch & check organization appointment
    if not update:
        rid = get_rid(input['organization_appointment'])
        organization_appointment = OrganizationAppointment.objects.filter(id=rid.id).first()
        result['organization_appointment'] = organization_appointment
        if not organization_appointment:
            raise Exception(_('Invalid Organization Appointment ID!'))

    # Fetch & check account
    rid = get_rid(input['acount'])
    account = Account.objects.filter(id=rid.id).first()
    result['account'] = account
    if not account:
        raise Exception(_('Invalid Account ID!'))

    # Fetch & check tax rate
    rid = get_rid(input['finance_tax_rate'])
    finance_tax_rate = FinanceTaxRate.objects.filter(id=rid.id).first()
    result['finance_tax_rate'] = finance_tax_rate
    if not finance_tax_rate:
        raise Exception(_('Invalid Finance Tax Rate ID!'))


    return result


class OrganizationAppointmentPriceNodeInterface(graphene.Interface):
    id = graphene.GlobalID()
    price_display = graphene.String()


class OrganizationAppointmentPriceNode(DjangoObjectType):
    class Meta:
        model = OrganizationAppointmentPrice
        filter_fields = {
            'organization_appointment': ['exact'],
            'date_start': ['lte'],
            'date_end': ['gte', 'isnull']
        }
        interfaces = (graphene.relay.Node, OrganizationAppointmentPriceNodeInterface)

    def resolve_price_display(self, info):
        from ..modules.finance_tools import display_float_as_amount
        return display_float_as_amount(self.price)

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_organizationappointmentprice')

        return self._meta.model.objects.get(id=id)


class OrganizationAppointmentPriceQuery(graphene.ObjectType):
    organization_appointment_prices = DjangoFilterConnectionField(OrganizationAppointmentPriceNode)
    organization_appointment_price = graphene.relay.Node.Field(OrganizationAppointmentPriceNode)

    def resolve_organization_appointment_prices(self, info, organization_appointment, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_organizationappointmentprice')

        rid = get_rid(organization_appointment)
        return OrganizationAppointmentPrice.objects.filter(organization_appointment=rid.id).order_by('-date_start')


class CreateOrganizationAppointmentPrice(graphene.relay.ClientIDMutation):
    class Input:
        organization_appointment = graphene.ID(required=True)
        price = graphene.Float(required=True, default_value=0)
        finance_tax_rate = graphene.ID(required=True)
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=False, default_value=None)
        

    organization_appointment_price = graphene.Field(OrganizationAppointmentPriceNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_organizationappointmentprice')

        result = validate_create_update_input(input, update=False)
        organization_appointment_price = OrganizationAppointmentPrice(
            organization_appointment = result['organization_appointment'],
            price = input['price'],
            finance_tax_rate = result['finance_tax_rate'],
            date_start = result['date_start'],
            date_end = result.get('date_end', None)
        )
        

        organization_appointment_price.save()

        return CreateOrganizationAppointmentPrice(organization_appointment_price=organization_appointment_price)


class UpdateOrganizationAppointmentPrice(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        price = graphene.Float(required=True, default_value=0)
        finance_tax_rate = graphene.ID(required=True)
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=False, default_value=None)
        
    organization_appointment_price = graphene.Field(OrganizationAppointmentPriceNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_organizationappointmentprice')

        rid = get_rid(input['id'])
        organization_appointment_price = OrganizationAppointmentPrice.objects.filter(id=rid.id).first()
        if not organization_appointment_price:
            raise Exception('Invalid Organization Appointment ID!')

        result = validate_create_update_input(input, update=True)

        organization_appointment_price.price = input['price']
        organization_appointment_price.finance_tax_rate = result['finance_tax_rate']
        organization_appointment_price.date_start = result['date_start']
        organization_appointment_price.date_end = result.get('date_end', None)
        organization_appointment_price.save(force_update=True)

        return UpdateOrganizationAppointmentPrice(organization_appointment_price=organization_appointment_price)


class DeleteOrganizationAppointmentPrice(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    # organization_appointment_price = graphene.Field(OrganizationAppointmentPriceNode)
    ok = graphene.Boolean()
    

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_organizationappointmentprice')

        rid = get_rid(input['id'])

        organization_appointment_price = OrganizationAppointmentPrice.objects.filter(id=rid.id).first()
        if not organization_appointment_price:
            raise Exception('Invalid Organization Appointment ID!')

        ok = organization_appointment_price.delete()

        return DeleteOrganizationAppointmentPrice(ok=ok)


class OrganizationAppointmentPriceMutation(graphene.ObjectType):
    delete_organization_appointment_price = DeleteOrganizationAppointmentPrice.Field()
    create_organization_appointment_price = CreateOrganizationAppointmentPrice.Field()
    update_organization_appointment_price = UpdateOrganizationAppointmentPrice.Field()
    