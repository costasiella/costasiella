from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import FinancePaymentBatch, FinancePaymentBatchCategory, OrganizationLocation
from ..models.choices.finance_payment_batch_statuses import get_finance_payment_batch_statuses
from ..models.choices.finance_payment_batch_types import get_finance_payment_batch_types
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

from .custom_schema_validators import is_year, is_month

from ..tasks import finance_payment_batch_generate_items_invoices


m = Messages()


class FinancePaymentBatchNode(DjangoObjectType):
    class Meta:
        model = FinancePaymentBatch
        filter_fields = ['batch_type']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_financepaymentbatch')

        return self._meta.model.objects.get(id=id)


class FinancePaymentBatchQuery(graphene.ObjectType):
    finance_payment_batches = DjangoFilterConnectionField(FinancePaymentBatchNode)
    finance_payment_batch = graphene.relay.Node.Field(FinancePaymentBatchNode)

    def resolve_finance_payment_batches(self, info, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_financepaymentbatch')

        return FinancePaymentBatch.objects.order_by('-created_at')


def validate_create_update_input(input, update=False):
    """
    Validate input
    """
    result = {}

    # Fetch & check invoice group
    if not update:
        # Create only
        # batch category
        if 'finance_payment_batch_category' in input:
            rid = get_rid(input['finance_payment_batch_category'])
            finance_payment_batch_category = FinancePaymentBatchCategory.objects.filter(id=rid.id).first()
            result['finance_payment_batch_category'] = finance_payment_batch_category
            if not finance_payment_batch_category:
                raise Exception(_('Invalid Finance Payment Batch Category ID!'))

        # location
        if 'organization_location' in input:
            rid = get_rid(input['organization_location'])
            organization_location = OrganizationLocation.objects.filter(id=rid.id).first()
            result['organization_location'] = organization_location
            if not organization_location:
                raise Exception(_('Invalid Organization Location ID!'))

        if 'year' in input:
            is_year(input['subscription_year'])
            result['subscription_year'] = input['subscription_year']

        if 'month' in input:
            is_month(input['subscription_month'])
            result['subscription_month'] = input['subscription_month']

        if 'batch_type' in input:
            batch_types = []
            for item in get_finance_payment_batch_types():
                batch_types.append(item[0])

            if input['batch_type'] not in batch_types:
                raise Exception(_('Invalid Finance Payment Batch Type!'))
    else:
        if 'status' in input:
            statuses = []
            for item in get_finance_payment_batch_statuses():
                statuses.append(item[0])

            if input['status'] not in statuses:
                raise Exception(_('Invalid Finance Payment Batch Status!'))

    return result


class CreateFinancePaymentBatch(graphene.relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        batch_type = graphene.String(required=True)
        finance_payment_batch_category = graphene.ID(required=False)
        description = graphene.String(required=False)
        year = graphene.Int(required=False)
        month = graphene.Int(required=False)
        execution_date = graphene.types.datetime.Date(required=True)
        include_zero_amounts = graphene.Boolean(required=False, default_value=False)
        organization_location = graphene.ID(required=False)
        note = graphene.String(required=False)

    finance_payment_batch = graphene.Field(FinancePaymentBatchNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_financepaymentbatch')

        validation_result = validate_create_update_input(input)

        finance_payment_batch = FinancePaymentBatch(
            name=input['name'],
            batch_type=input['batch_type'],
            execution_date=input['execution_date'],
        )

        if 'include_zero_amounts' in input:
            finance_payment_batch.include_zero_amounts = input['include_zero_amounts']

        if 'note' in input:
            finance_payment_batch.note = input['note']

        if 'finance_payment_batch_category' in validation_result:
            finance_payment_batch.finance_payment_batch_category = validation_result['finance_payment_batch_category']

        if 'organization_location' in validation_result:
            finance_payment_batch.organization_location = validation_result['organization_location']

        if 'year' in validation_result:
            finance_payment_batch.year = validation_result['year']

        if 'month' in validation_result:
            finance_payment_batch.month = validation_result['month']

        finance_payment_batch.save()

        # Call background task to create batch items
        task = finance_payment_batch_generate_items_invoices.delay(finance_payment_batch.id)

        return CreateFinancePaymentBatch(finance_payment_batch=finance_payment_batch)


class UpdateFinancePaymentBatch(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=False)
        status = graphene.String(required=False)
        note = graphene.String(required=False)

    finance_payment_batch = graphene.Field(FinancePaymentBatchNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_financepaymentbatch')

        rid = get_rid(input['id'])
        finance_payment_batch = FinancePaymentBatch.objects.filter(id=rid.id).first()
        if not finance_payment_batch:
            raise Exception('Invalid Finance Payment Batch Category ID!')

        validation_result = validate_create_update_input(input, update=True)
        finance_payment_batch.name = input['name']

        if 'note' in input:
            finance_payment_batch.note = input['note']

        if 'status' in validation_result:
            finance_payment_batch.status = validation_result['status']

        finance_payment_batch.save()

        return UpdateFinancePaymentBatch(finance_payment_batch=finance_payment_batch)


class DeleteFinancePaymentBatch(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_financepaymentbatch')

        rid = get_rid(input['id'])

        finance_payment_batch = FinancePaymentBatch.objects.filter(id=rid.id).first()
        if not finance_payment_batch:
            raise Exception(_('Invalid Finance Payment Batch ID!'))

        ok = finance_payment_batch.delete()

        return DeleteFinancePaymentBatch(ok=ok)


class FinancePaymentBatchMutation(graphene.ObjectType):
    delete_finance_payment_batch = DeleteFinancePaymentBatch.Field()
    create_finance_payment_batch = CreateFinancePaymentBatch.Field()
    update_finance_payment_batch = UpdateFinancePaymentBatch.Field()
