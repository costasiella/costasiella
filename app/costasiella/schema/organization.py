from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import Organization
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class OrganizationNode(DjangoObjectType):
    class Meta:
        model = Organization
        filter_fields = ['archived', 'id']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_organization')

        return self._meta.model.objects.get(id=id)


class OrganizationQuery(graphene.ObjectType):
    organizations = DjangoFilterConnectionField(OrganizationNode)
    organization = graphene.relay.Node.Field(OrganizationNode)

    def resolve_organization(self, info, archived=False, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_organization')

        ## return everything:
        # if user.has_perm('costasiella.view_organization'):
        return Organization.objects.filter(archived = archived).order_by('name')

        # return None


class CreateOrganization(graphene.relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        address = graphene.String(required=False)
        phone = graphene.String(required=False)
        email = graphene.String(required=False)
        registration = graphene.String(required=False)
        tax_registration = graphene.String(required=False)


    organization = graphene.Field(OrganizationNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_organization')

        organization = Organization(
            name=input['name'], 
        )

        if 'address' in input:
            organization.address = input['address']

        if 'phone' in input:
            organization.phone = input['phone']

        if 'email' in input:
            organization.email = input['email']

        if 'registration' in input:
            organization.registration = input['registration']

        if 'tax_registration' in input:
            organization.tax_registration = input['tax_registration']

        organization.save()

        return CreateOrganization(organization=organization)


class UpdateOrganization(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        address = graphene.String(required=False)
        phone = graphene.String(required=False)
        email = graphene.String(required=False)
        registration = graphene.String(required=False)
        tax_registration = graphene.String(required=False)
        
    organization = graphene.Field(OrganizationNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_organization')

        rid = get_rid(input['id'])

        organization = Organization.objects.filter(id=rid.id).first()
        if not organization:
            raise Exception('Invalid Organization ID!')

        if 'name' in input:
            organization.name = input['name']

        if 'address' in input:
            organization.address = input['address']

        if 'phone' in input:
            organization.phone = input['phone']

        if 'email' in input:
            organization.email = input['email']

        if 'registration' in input:
            organization.registration = input['registration']

        if 'tax_registration' in input:
            organization.tax_registration = input['tax_registration']

        organization.save()

        return UpdateOrganization(organization=organization)


# class ArchiveOrganization(graphene.relay.ClientIDMutation):
#     class Input:
#         id = graphene.ID(required=True)
#         archived = graphene.Boolean(required=True)

#     organization = graphene.Field(OrganizationNode)

#     @classmethod
#     def mutate_and_get_payload(self, root, info, **input):
#         user = info.context.user
#         require_login_and_permission(user, 'costasiella.delete_organization')

#         rid = get_rid(input['id'])

#         organization = Organization.objects.filter(id=rid.id).first()
#         if not organization:
#             raise Exception('Invalid Organization  ID!')

#         organization.archived = input['archived']
#         organization.save(force_update=True)

#         return ArchiveOrganization(organization=organization)


class OrganizationMutation(graphene.ObjectType):
    # archive_organization = ArchiveOrganization.Field()
    create_organization = CreateOrganization.Field()
    update_organization = UpdateOrganization.Field()