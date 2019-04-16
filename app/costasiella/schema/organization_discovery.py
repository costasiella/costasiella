from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import SchoolDiscovery
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class SchoolDiscoveryNode(DjangoObjectType):
    class Meta:
        model = SchoolDiscovery
        filter_fields = ['archived']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_schooldiscovery')

        return self._meta.model.objects.get(id=id)


class SchoolDiscoveryQuery(graphene.ObjectType):
    school_discoveries = DjangoFilterConnectionField(SchoolDiscoveryNode)
    school_discovery = graphene.relay.Node.Field(SchoolDiscoveryNode)

    def resolve_school_discoveries(self, info, archived=False, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_schooldiscovery')

        ## return everything:
        # if user.has_perm('costasiella.view_schooldiscovery'):
        return SchoolDiscovery.objects.filter(archived = archived).order_by('name')

        # return None


class CreateSchoolDiscovery(graphene.relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)

    school_discovery = graphene.Field(SchoolDiscoveryNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_schooldiscovery')

        errors = []
        if not len(input['name']):
            print('validation error found')
            raise GraphQLError(_('Name is required'))

        school_discovery = SchoolDiscovery(
            name=input['name'], 
        )

        school_discovery.save()

        return CreateSchoolDiscovery(school_discovery=school_discovery)


class UpdateSchoolDiscovery(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        
    school_discovery = graphene.Field(SchoolDiscoveryNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_schooldiscovery')

        rid = get_rid(input['id'])

        school_discovery = SchoolDiscovery.objects.filter(id=rid.id).first()
        if not school_discovery:
            raise Exception('Invalid School Discovery ID!')

        school_discovery.name = input['name']
        school_discovery.save(force_update=True)

        return UpdateSchoolDiscovery(school_discovery=school_discovery)


class ArchiveSchoolDiscovery(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    school_discovery = graphene.Field(SchoolDiscoveryNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_schooldiscovery')

        rid = get_rid(input['id'])

        school_discovery = SchoolDiscovery.objects.filter(id=rid.id).first()
        if not school_discovery:
            raise Exception('Invalid School Discovery ID!')

        school_discovery.archived = input['archived']
        school_discovery.save(force_update=True)

        return ArchiveSchoolDiscovery(school_discovery=school_discovery)


class SchoolDiscoveryMutation(graphene.ObjectType):
    archive_school_discovery = ArchiveSchoolDiscovery.Field()
    create_school_discovery = CreateSchoolDiscovery.Field()
    update_school_discovery = UpdateSchoolDiscovery.Field()