from django.utils.translation import gettext as _
from django.conf import settings

import os
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

from ..tasks import finance_payment_batch_generate_items, finance_payment_batch_add_invoice_payments


m = Messages()


class FinancePaymentBatchNodeInterface(graphene.Interface):
    id = graphene.GlobalID()
    total_display = graphene.String()


class FinancePaymentBatchNode(DjangoObjectType):
    class Meta:
        model = FinancePaymentBatch
        fields = (
            'name',
            'batch_type',
            'finance_payment_batch_category',
            'status',
            'description',
            'year',
            'month',
            'execution_date',
            'include_zero_amounts',
            'note',
            'total',
            'count_items',
            'created_at',
            'updated_at',
            # Reverse relations
            'exports',
            'items'
        )
        filter_fields = ['batch_type']
        interfaces = (graphene.relay.Node, FinancePaymentBatchNodeInterface,)

    def resolve_total_display(self, info):
        from ..modules.finance_tools import display_float_as_amount
        return display_float_as_amount(self.total)

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
            is_year(input['year'])
            result['year'] = input['year']

        if 'month' in input:
            is_month(input['month'])
            result['month'] = input['month']

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

            result['status'] = input['status']

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
        # organization_location = graphene.ID(required=False)
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

        if 'description' in input:
            finance_payment_batch.description = input['description']

        if 'finance_payment_batch_category' in validation_result:
            finance_payment_batch.finance_payment_batch_category = validation_result['finance_payment_batch_category']

        # if 'organization_location' in validation_result:
        #     finance_payment_batch.organization_location = validation_result['organization_location']

        if 'year' in validation_result:
            finance_payment_batch.year = validation_result['year']

        if 'month' in validation_result:
            finance_payment_batch.month = validation_result['month']

        finance_payment_batch.save()

        # Call background task to create batch items when we're not in CI test mode
        if 'GITHUB_WORKFLOW' not in os.environ and not getattr(settings, 'TESTING', False):
            task = finance_payment_batch_generate_items.delay(finance_payment_batch.id)

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
        if 'name' in input:
            finance_payment_batch.name = input['name']

        if 'note' in input:
            finance_payment_batch.note = input['note']

        if 'status' in validation_result:
            if finance_payment_batch.status == 'SENT_TO_BANK':
                raise Exception(_("Unable to change status from sent to bank"))

            finance_payment_batch.status = validation_result['status']

            if finance_payment_batch.status == "SENT_TO_BANK" and \
                    not finance_payment_batch.finance_payment_batch_category:
                # First time batch status has been changed to SENT_TO_BANK; generate items
                task = finance_payment_batch_add_invoice_payments.delay(finance_payment_batch.id)

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

        ok = bool(finance_payment_batch.delete())

        return DeleteFinancePaymentBatch(ok=ok)


class FinancePaymentBatchMutation(graphene.ObjectType):
    delete_finance_payment_batch = DeleteFinancePaymentBatch.Field()
    create_finance_payment_batch = CreateFinancePaymentBatch.Field()
    update_finance_payment_batch = UpdateFinancePaymentBatch.Field()
