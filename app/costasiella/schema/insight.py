from django.utils.translation import gettext as _
from django.db.models import Q, FilteredRelation, OuterRef, Subquery

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from graphql_relay import to_global_id

from ..models import ScheduleItem, ScheduleItemWeeklyOTC, OrganizationClasstype, OrganizationLevel, OrganizationLocationRoom
from ..modules.gql_tools import require_login_and_permission, require_login_and_one_of_permissions, get_rid
from ..modules.messages import Messages
from ..modules.model_helpers.schedule_item_helper import ScheduleItemHelper
from .account import AccountNode
from .organization_classtype import OrganizationClasstypeNode
from .organization_level import OrganizationLevelNode
from .organization_location_room import OrganizationLocationRoomNode
from .schedule_item import ScheduleItemNode

from ..dudes.insight_data_dude import InsightDataDude


m = Messages()

import datetime


class AccountClasspassesSoldType(graphene.ObjectType):
    description = graphene.String()
    data = graphene.List(graphene.Int())
    year = graphene.Int()

    def resolve_description(self, info):
        return self.description = _("account_classpasses_sold")

    def resolve_data(self, info):       
        insight_data_dude = InsightDataDude()
        data = insight_data_dude.get_classpasses_year_summary_count(year)

        return data


def validate_schedule_classes_query_date_input(date_from, 
                                               date_until, 
                                               order_by, 
                                               organization_classtype,
                                               organization_level,
                                               organization_location,
                                               ):
    """
    Check if date_until >= date_start
    Check if delta between dates <= 7 days
    """
    result = {}

    if date_until < date_from:
        raise Exception(_("dateUntil has to be bigger then dateFrom"))

    days_between = (date_until - date_from).days
    if days_between > 6:
        raise Exception(_("dateFrom and dateUntil can't be more then 7 days apart")) 
    
    if order_by:
        sort_options = [
            'location',
            'starttime'
        ]  
        if order_by not in sort_options:
            raise Exception(_("orderBy can only be 'location' or 'starttime'")) 


    print("###########")
    print(organization_location)

    if organization_classtype:
        rid = get_rid(organization_classtype)
        organization_classtype_id = rid.id
        result['organization_classtype_id'] = organization_classtype_id

    if organization_level:
        rid = get_rid(organization_level)
        organization_level_id = rid.id
        result['organization_level_id'] = organization_level_id

    if organization_location:
        rid = get_rid(organization_location)
        organization_location_id = rid.id
        result['organization_location_id'] = organization_location_id

    return result


class InsightQuery(graphene.ObjectType):
    account_classpasses_sold = graphene.List(
        AccountClasspassesSoldType,
        year=graphene.Int,
    )

    def resolve_account_classpasses_sold(self, 
                                         info, 
                                         year=graphene.Int(required=True, default_value=datetime.date.today().year):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_insightclasspassessold')

        print('############ resolve')
        print(locals())
        print(organization_location)

        account_classpasses_sold = AccountClasspassesSoldType()
        account_classpasses_sold.year = year

        return account_classpasses_sold
