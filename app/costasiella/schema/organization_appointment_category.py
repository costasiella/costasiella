from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import OrganizationAppointmentCategory, OrganizationAppointmentCategoryRoom
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()

class OrganizationAppointmentCategoryNode(DjangoObjectType):
    class Meta:
        model = OrganizationAppointmentCategory
        filter_fields = ['archived']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        print("info:")
        print(info)
        user = info.context.user
        print('user authenticated:')
        print(user.is_authenticated)
        print(user)
        print(user.is_anonymous)
        require_login_and_permission(user, 'costasiella.view_organizationappointmentcategory')

        # Return only public non-archived locations
        return self._meta.model.objects.get(id=id)


# class ValidationErrorMessage(graphene.ObjectType):
#     field = graphene.String(required=True)
#     message = graphene.String(required=True)


# class ValidationErrors(graphene.ObjectType):
# 	validation_errors = graphene.List(ValidationErrorMessage)
#     # error_message = graphene.String(required=True)


class OrganizationAppointmentCategoryQuery(graphene.ObjectType):
    organization_appointment_categories = DjangoFilterConnectionField(OrganizationAppointmentCategoryNode)
    organization_appointment_category = graphene.relay.Node.Field(OrganizationAppointmentCategoryNode)

    def resolve_organization_appointment_categories(self, info, archived=False, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception(m.user_not_logged_in)

        if user.has_perm('costasiella.view_organizationappointmentcategory'):
            print('user has view permission')
            return OrganizationAppointmentCategory.objects.filter(archived = archived).order_by('name')

        # Return only public non-archived locations
        return OrganizationAppointmentCategory.objects.filter(display_public = True, archived = False).order_by('name')


class CreateOrganizationAppointmentCategory(graphene.relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        display_public = graphene.Boolean(required=True)

    organization_appointment_category = graphene.Field(OrganizationAppointmentCategoryNode)

    # Output = CreateOrganizationAppointmentCategoryPayload

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_organizationappointmentcategory')

        errors = []
        if not len(input['name']):
            print('validation error found')
            raise GraphQLError(_('Name is required'))
            # errors.append(
            #     ValidationErrorMessage(
            #         field="name",
            #         message=_("Name is required")
            #     )
            # )

            # return ValidationErrors(
            #     validation_errors = errors
            # )

        organization_appointment_category = OrganizationAppointmentCategory(
            name=input['name'], 
            display_public=input['display_public']
        )
        organization_appointment_category.save()

        # return CreateOrganizationAppointmentCategorySuccess(organization_appointment_category=organization_appointment_category)
        return CreateOrganizationAppointmentCategory(organization_appointment_category=organization_appointment_category)


# ''' Query like this when enabling error output using union:
# mutation {
#   createOrganizationAppointmentCategory(name:"", displayPublic:true) {
#     __typename
#     ... on CreateOrganizationAppointmentCategorySuccess {
#       organizationAppointmentCategory {
#         id
#         name
#       }
#     }
#     ... on ValidationErrors {
#       validationErrors {
#         field
#         message
#       }
#     }
#   }
# }

# '''

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
        organization_appointment_category.save(force_update=True)

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
        organization_appointment_category.save(force_update=True)

        return ArchiveOrganizationAppointmentCategory(organization_appointment_category=organization_appointment_category)


class OrganizationAppointmentCategoryMutation(graphene.ObjectType):
    archive_organization_appointment_category = ArchiveOrganizationAppointmentCategory.Field()
    create_organization_appointment_category = CreateOrganizationAppointmentCategory.Field()
    update_organization_appointment_category = UpdateOrganizationAppointmentCategory.Field()