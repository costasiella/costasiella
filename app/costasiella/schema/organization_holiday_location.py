from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import OrganizationHoliday, OrganizationLocation, OrganizationHolidayLocation
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class OrganizationHolidayLocationNode(DjangoObjectType):
    class Meta:
        model = OrganizationHolidayLocation
        fields = (
            'organization_holiday',
            'organization_location'
        )
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_organizationholidaylocation')

        return self._meta.model.objects.get(id=id)


class CreateOrganizationHolidayLocation(graphene.relay.ClientIDMutation):
    class Input:
        organization_holiday = graphene.ID(required=True)
        organization_location = graphene.ID(required=True)

    organization_holiday_location = graphene.Field(OrganizationHolidayLocationNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_organizationholidaylocation')

        rid_holiday = get_rid(input['organization_holiday'])
        rid_location = get_rid(input['organization_location'])

        organization_holiday = OrganizationHoliday.objects.get(pk=rid_holiday.id)
        organization_location = OrganizationLocation.objects.get(pk=rid_location.id)

        query_set = OrganizationHolidayLocation.objects.filter(
            organization_holiday = organization_holiday,
            organization_location = organization_location
        )

        # Don't insert duplicate records in the DB. If this records exist, fetch and return it
        if not query_set.exists():
            organization_holiday_location = OrganizationHolidayLocation(
                organization_holiday=organization_holiday,
                organization_location=organization_location
            )

            organization_holiday_location.save()
        else:
            organization_holiday_location = query_set.first()

        return CreateOrganizationHolidayLocation(organization_holiday_location=organization_holiday_location)


class DeleteOrganizationHolidayLocation(graphene.relay.ClientIDMutation):
    class Input:
        # id = graphene.ID(required=True)
        organization_holiday = graphene.ID(required=True)
        organization_location = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_organizationholidaylocation')

        # rid = get_rid(input['id'])
        rid_holiday = get_rid(input['organization_holiday'])
        rid_location = get_rid(input['organization_location'])

        organization_holiday = OrganizationHoliday.objects.get(pk=rid_holiday.id)
        organization_location = OrganizationLocation.objects.get(pk=rid_location.id)

        organization_holiday_location = OrganizationHolidayLocation.objects.filter(
            organization_holiday = organization_holiday,
            organization_location = organization_location
        ).first()

        ok = bool(organization_holiday_location.delete())

        return DeleteOrganizationHolidayLocation(
            ok=ok
        )


class OrganizationHolidayLocationMutation(graphene.ObjectType):
    create_organization_holiday_location = CreateOrganizationHolidayLocation.Field()
    delete_organization_holiday_location = DeleteOrganizationHolidayLocation.Field()