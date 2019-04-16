from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import SchoolClasspassGroup
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class SchoolClasspassGroupNode(DjangoObjectType):
    class Meta:
        model = SchoolClasspassGroup
        filter_fields = ['archived']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_schoolclasspassgroup')

        return self._meta.model.objects.get(id=id)


class SchoolClasspassGroupQuery(graphene.ObjectType):
    school_classpass_groups = DjangoFilterConnectionField(SchoolClasspassGroupNode)
    school_classpass_group = graphene.relay.Node.Field(SchoolClasspassGroupNode)

    def resolve_school_classpass_groups(self, info, archived=False, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_schoolclasspassgroup')

        ## return everything:
        return SchoolClasspassGroup.objects.filter(archived = archived).order_by('name')


class CreateSchoolClasspassGroup(graphene.relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)

    school_classpass_group = graphene.Field(SchoolClasspassGroupNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_schoolclasspassgroup')

        errors = []
        if not len(input['name']):
            print('validation error found')
            raise GraphQLError(_('Name is required'))

        school_classpass_group = SchoolClasspassGroup(
            name=input['name'], 
        )

        school_classpass_group.save()

        return CreateSchoolClasspassGroup(school_classpass_group=school_classpass_group)


class UpdateSchoolClasspassGroup(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        
    school_classpass_group = graphene.Field(SchoolClasspassGroupNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_schoolclasspassgroup')

        rid = get_rid(input['id'])

        school_classpass_group = SchoolClasspassGroup.objects.filter(id=rid.id).first()
        if not school_classpass_group:
            raise Exception('Invalid School Classpass Group ID!')

        school_classpass_group.name = input['name']
        school_classpass_group.save(force_update=True)

        return UpdateSchoolClasspassGroup(school_classpass_group=school_classpass_group)


class ArchiveSchoolClasspassGroup(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    school_classpass_group = graphene.Field(SchoolClasspassGroupNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_schoolclasspassgroup')

        rid = get_rid(input['id'])

        school_classpass_group = SchoolClasspassGroup.objects.filter(id=rid.id).first()
        if not school_classpass_group:
            raise Exception('Invalid School Classpass Group ID!')

        school_classpass_group.archived = input['archived']
        school_classpass_group.save(force_update=True)

        return ArchiveSchoolClasspassGroup(school_classpass_group=school_classpass_group)


class SchoolClasspassGroupMutation(graphene.ObjectType):
    archive_school_classpass_group = ArchiveSchoolClasspassGroup.Field()
    create_school_classpass_group = CreateSchoolClasspassGroup.Field()
    update_school_classpass_group = UpdateSchoolClasspassGroup.Field()