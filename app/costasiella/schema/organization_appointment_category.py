from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import OrganizationAppointmentCategory 
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class OrganizationAppointmentCategoryNode(DjangoObjectType):
    class Meta:
        model = OrganizationAppointmentCategory
        fields = (
            'archived',
            'display_public',
            'name'
        )
        filter_fields = ['archived']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_organizationappointmentcategory')

        # Return only public non-archived locations
        return self._meta.model.objects.get(id=id)


class OrganizationAppointmentCategoryQuery(graphene.ObjectType):
    organization_appointment_categories = DjangoFilterConnectionField(OrganizationAppointmentCategoryNode)
    organization_appointment_category = graphene.relay.Node.Field(OrganizationAppointmentCategoryNode)

    def resolve_organization_appointment_categories(self, info, archived=False, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception(m.user_not_logged_in)

        if user.has_perm('costasiella.view_organizationappointmentcategory'):
            return OrganizationAppointmentCategory.objects.filter(archived = archived).order_by('name')

        # Return only public non-archived locations
        return OrganizationAppointmentCategory.objects.filter(display_public = True, archived = False).order_by('name')


class CreateOrganizationAppointmentCategory(graphene.relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        display_public = graphene.Boolean(required=True, default_value=True)

    organization_appointment_category = graphene.Field(OrganizationAppointmentCategoryNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_organizationappointmentcategory')

        errors = []
        if not len(input['name']):
            raise GraphQLError(_('Name is required'))

        organization_appointment_category = OrganizationAppointmentCategory(
            name=input['name'], 
            display_public=input['display_public']
        )
        organization_appointment_category.save()

        return CreateOrganizationAppointmentCategory(organization_appointment_category=organization_appointment_category)


class UpdateOrganizationAppointmentCategory(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        display_public = graphene.Boolean(required=True)
        
    organization_appointment_category = graphene.Field(OrganizationAppointmentCategoryNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_organizationappointmentcategory')

        rid = get_rid(input['id'])

        organization_appointment_category = OrganizationAppointmentCategory.objects.filter(id=rid.id).first()
        if not organization_appointment_category:
            raise Exception('Invalid Organization AppointmentCategory ID!')

        organization_appointment_category.name = input['name']
        organization_appointment_category.display_public = input['display_public']
        organization_appointment_category.save()

        return UpdateOrganizationAppointmentCategory(organization_appointment_category=organization_appointment_category)


class ArchiveOrganizationAppointmentCategory(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    organization_appointment_category = graphene.Field(OrganizationAppointmentCategoryNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_organizationappointmentcategory')

        rid = get_rid(input['id'])

        organization_appointment_category = OrganizationAppointmentCategory.objects.filter(id=rid.id).first()
        if not organization_appointment_category:
            raise Exception('Invalid Organization AppointmentCategory ID!')

        organization_appointment_category.archived = input['archived']
        organization_appointment_category.save()

        return ArchiveOrganizationAppointmentCategory(organization_appointment_category=organization_appointment_category)


class OrganizationAppointmentCategoryMutation(graphene.ObjectType):
    archive_organization_appointment_category = ArchiveOrganizationAppointmentCategory.Field()
    create_organization_appointment_category = CreateOrganizationAppointmentCategory.Field()
    update_organization_appointment_category = UpdateOrganizationAppointmentCategory.Field()