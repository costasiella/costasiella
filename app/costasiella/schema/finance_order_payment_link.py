from django.utils.translation import gettext as _
from django.db.models import Q, FilteredRelation, OuterRef, Subquery

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from graphql_relay import to_global_id

from ..models import FinanceOrder
from ..modules.gql_tools import require_login_and_permission, require_login_and_one_of_permissions, get_rid
from ..modules.messages import Messages


m = Messages()

import datetime


# ScheduleClassType
class FinanceOrderPaymentLinkType(graphene.ObjectType):
    payment_link = graphene.String()


class CreateFinanceOrderPaymentLink(graphene.Mutation):
    class Arguments:
        id = graphene.ID() # FinanceOrderID

    finance_order_payment_link = graphene.Field(FinanceOrderPaymentLinkType)

    @classmethod
    def mutate(self, root, info, id):
        user = info.context.user
        # Check if the user owns this order
        print(id)

        rid = get_rid(id)
        finance_order = FinanceOrder.objects.get(pk=rid.id)      

        


        return CreateFinanceOrderPaymentLink(
            finance_order_payment_link=finance_order_payment_link
        )


class FinanceOrderPaymentLinkMutation(graphene.ObjectType):
    create_finance_order_payment_link = CreateFinanceOrderPaymentLink.Field()