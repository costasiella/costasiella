from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import OrganizationAppointmentCategory, OrganizationAppointment
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()

class OrganizationAppointmentNode(DjangoObjectType):
    class Meta:
        model = OrganizationAppointment
        filter_fields = ['archived', 'organization_appointment_category']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_organizationappointment')

        # Return only public non-archived appointment_category rooms
        return self._meta.model.objects.get(id=id)


class OrganizationAppointmentQuery(graphene.ObjectType):
    organization_appointments = DjangoFilterConnectionField(OrganizationAppointmentNode)
    organization_appointment = graphene.relay.Node.Field(OrganizationAppointmentNode)

    def resolve_organization_appointments(self, info, archived=False, **kwargs):
        user = info.context.user

        if user.is_anonymous:
            raise Exception(m.user_not_logged_in)

        ## return everything:
        if user.has_perm('costasiella.view_organizationappointment'):
            return OrganizationAppointment.objects.filter(archived = archived).order_by('organization_appointment_category__name', 'name')

        # Return only public non-archived rooms
        return OrganizationAppointment.objects.filter(display_public = True, archived = False).order_by('organization_appointment_category__name', 'name')
            

class CreateOrganizationAppointment(graphene.relay.ClientIDMutation):
    class Input:
        organization_appointment_category = graphene.ID(required=True)
        name = graphene.String(required=True)
        display_public = graphene.Boolean(required=True)

    organization_appointment = graphene.Field(OrganizationAppointmentNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_organizationappointment')

        if not len(input['name']):
            raise GraphQLError(_('Name is required'))

        rid = get_rid(input['organization_appointment_category'])
        organization_appointment_category = OrganizationAppointmentCategory.objects.filter(id=rid.id).first()
        if not organization_appointment_category:
            raise Exception('Invalid Organization Appointment Category ID!')

        organization_appointment = OrganizationAppointment(
            organization_appointment_category = organization_appointment_category,
            name=input['name'], 
            display_public=input['display_public']
        )
        organization_appointment.save()

        return CreateOrganizationAppointment(organization_appointment=organization_appointment)


class UpdateOrganizationAppointment(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        display_public = graphene.Boolean(required=True)
        
    organization_appointment = graphene.Field(OrganizationAppointmentNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_organizationappointment')

        rid = get_rid(input['id'])

        organization_appointment = OrganizationAppointment.objects.filter(id=rid.id).first()
        if not organization_appointment:
            raise Exception('Invalid Organization Appointment ID!')

        organization_appointment.name = input['name']
        organization_appointment.display_public = input['display_public']
        organization_appointment.save()

        return UpdateOrganizationAppointment(organization_appointment=organization_appointment)


class ArchiveOrganizationAppointment(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    organization_appointment = graphene.Field(OrganizationAppointmentNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_organizationappointment')

        rid = get_rid(input['id'])

        organization_appointment = OrganizationAppointment.objects.filter(id=rid.id).first()
        if not organization_appointment:
            raise Exception('Invalid Organization AppointmentCategory Room ID!')

        organization_appointment.archived = input['archived']
        organization_appointment.save()

        return ArchiveOrganizationAppointment(organization_appointment=organization_appointment)


class OrganizationAppointmentMutation(graphene.ObjectType):
    archive_organization_appointment = ArchiveOrganizationAppointment.Field()
    create_organization_appointment = CreateOrganizationAppointment.Field()
    update_organization_appointment = UpdateOrganizationAppointment.Field()
    