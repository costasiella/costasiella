from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import OrganizationLanguage
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class OrganizationLanguageNode(DjangoObjectType):
    class Meta:
        model = OrganizationLanguage
        fields = (
            'archived',
            'name'
        )
        filter_fields = ['archived']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_organizationlanguage')

        return self._meta.model.objects.get(id=id)


class OrganizationLanguageQuery(graphene.ObjectType):
    organization_languages = DjangoFilterConnectionField(OrganizationLanguageNode)
    organization_language = graphene.relay.Node.Field(OrganizationLanguageNode)

    def resolve_organization_languages(self, info, archived=False, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_organizationlanguage')

        ## return everything:
        # if user.has_perm('costasiella.view_organizationlanguage'):
        return OrganizationLanguage.objects.filter(archived = archived).order_by('name')

        # return None


class CreateOrganizationLanguage(graphene.relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)

    organization_language = graphene.Field(OrganizationLanguageNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_organizationlanguage')

        errors = []
        if not len(input['name']):
            raise GraphQLError(_('Name is required'))

        organization_language = OrganizationLanguage(
            name=input['name'], 
        )

        organization_language.save()

        return CreateOrganizationLanguage(organization_language=organization_language)


class UpdateOrganizationLanguage(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        
    organization_language = graphene.Field(OrganizationLanguageNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_organizationlanguage')

        rid = get_rid(input['id'])

        organization_language = OrganizationLanguage.objects.filter(id=rid.id).first()
        if not organization_language:
            raise Exception('Invalid Organization Language ID!')

        organization_language.name = input['name']
        organization_language.save(force_update=True)

        return UpdateOrganizationLanguage(organization_language=organization_language)


class ArchiveOrganizationLanguage(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    organization_language = graphene.Field(OrganizationLanguageNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_organizationlanguage')

        rid = get_rid(input['id'])

        organization_language = OrganizationLanguage.objects.filter(id=rid.id).first()
        if not organization_language:
            raise Exception('Invalid Organization Language ID!')

        organization_language.archived = input['archived']
        organization_language.save()

        return ArchiveOrganizationLanguage(organization_language=organization_language)


class OrganizationLanguageMutation(graphene.ObjectType):
    archive_organization_language = ArchiveOrganizationLanguage.Field()
    create_organization_language = CreateOrganizationLanguage.Field()
    update_organization_language = UpdateOrganizationLanguage.Field()