from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import OrganizationHoliday
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class OrganizationHolidayNode(DjangoObjectType):
    class Meta:
        model = OrganizationHoliday
        fields = (
            'name',
            'description',
            'date_start',
            'date_end',
            'classes',
            'organization_locations'
        )
        filter_fields = []
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user

        organization_holiday = self._meta.model.objects.get(id=id)
        if info.path.typename == "OrganizationHolidayLocationNode":
            return organization_holiday

        require_login_and_permission(user, 'costasiella.view_organizationholiday')

        return organization_holiday


class OrganizationHolidayQuery(graphene.ObjectType):
    organization_holidays = DjangoFilterConnectionField(OrganizationHolidayNode)
    organization_holiday = graphene.relay.Node.Field(OrganizationHolidayNode)

    def resolve_organization_holidays(self, info, archived=False, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_organizationholiday')

        return OrganizationHoliday.objects.all().order_by('date_start')


class CreateOrganizationHoliday(graphene.relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        description = graphene.String(required=False)
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=True)
        classes = graphene.Boolean(required=False)

    organization_holiday = graphene.Field(OrganizationHolidayNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_organizationholiday')

        organization_holiday = OrganizationHoliday(
            name=input['name'],
            date_start=input['date_start'],
            date_end=input['date_end']
        )

        if 'description' in input:
            organization_holiday.description = input['description']

        if 'classes' in input:
            organization_holiday.classes = input['classes']

        organization_holiday.save()

        return CreateOrganizationHoliday(organization_holiday=organization_holiday)


class UpdateOrganizationHoliday(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=False)
        description = graphene.String(required=False)
        date_start = graphene.types.datetime.Date(required=False)
        date_end = graphene.types.datetime.Date(required=False)
        classes = graphene.Boolean(required=False)

    organization_holiday = graphene.Field(OrganizationHolidayNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_organizationholiday')

        rid = get_rid(input['id'])

        organization_holiday = OrganizationHoliday.objects.filter(id=rid.id).first()
        if not organization_holiday:
            raise Exception('Invalid Organization Holiday ID!')

        if 'name' in input:
            organization_holiday.name = input['name']

        if 'description' in input:
            organization_holiday.description = input['description']

        if 'date_start' in input:
            organization_holiday.date_start = input['date_start']

        if 'date_end' in input:
            organization_holiday.date_end = input['date_end']

        if 'classes' in input:
            organization_holiday.classes = input['classes']

        organization_holiday.save()

        return UpdateOrganizationHoliday(organization_holiday=organization_holiday)


class DeleteOrganizationHoliday(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_organizationholiday')

        rid = get_rid(input['id'])
        organization_holiday = OrganizationHoliday.objects.filter(id=rid.id).first()
        if not organization_holiday:
            raise Exception('Invalid Organization Holiday ID!')

        ok = bool(organization_holiday.delete())

        return DeleteOrganizationHoliday(ok=ok)


class OrganizationHolidayMutation(graphene.ObjectType):
    delete_organization_holiday = DeleteOrganizationHoliday.Field()
    create_organization_holiday = CreateOrganizationHoliday.Field()
    update_organization_holiday = UpdateOrganizationHoliday.Field()