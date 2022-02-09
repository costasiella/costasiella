from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import FinancePaymentBatchExport
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class FinancePaymentBatchExportNode(DjangoObjectType):
    class Meta:
        model = FinancePaymentBatchExport
        fields = (
            'finance_payment_batch',
            'account',
            'created_at'
        )
        filter_fields = ['finance_payment_batch']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_financepaymentbatchexport')

        return self._meta.model.objects.get(id=id)


class FinancePaymentBatchExportQuery(graphene.ObjectType):
    finance_payment_batch_exports = DjangoFilterConnectionField(FinancePaymentBatchExportNode)
    finance_payment_batch_export = graphene.relay.Node.Field(FinancePaymentBatchExportNode)

    def resolve_finance_payment_batch_exports(self, info, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_financepaymentbatchexport')

        return FinancePaymentBatchExport.objects.all()
#
# NOTE: Exports are generated, no user interaction is implemented.
#
# def validate_create_update_input(input, update=False):
#     """
#     Validate input
#     """
#     result = {}
#
#     # Fetch & check invoice group
#     if not update:
#         # Create only
#         # batch category
#         if 'finance_payment_batch_category' in input:
#             rid = get_rid(input['finance_payment_batch_category'])
#             finance_payment_batch_category = FinancePaymentBatchCategory.objects.filter(id=rid.id).first()
#             result['finance_payment_batch_category'] = finance_payment_batch_category
#             if not finance_payment_batch_category:
#                 raise Exception(_('Invalid Finance Payment Batch Category ID!'))
#
#         # location
#         if 'organization_location' in input:
#             rid = get_rid(input['organization_location'])
#             organization_location = OrganizationLocation.objects.filter(id=rid.id).first()
#             result['organization_location'] = organization_location
#             if not organization_location:
#                 raise Exception(_('Invalid Organization Location ID!'))
#
#         if 'year' in input:
#             is_year(input['subscription_year'])
#             result['subscription_year'] = input['subscription_year']
#
#         if 'month' in input:
#             is_month(input['subscription_month'])
#             result['subscription_month'] = input['subscription_month']
#
#         if 'batch_type' in input:
#             batch_types = []
#             for export in get_finance_payment_batch_types():
#                 batch_types.append(export[0])
#
#             if input['batch_type'] not in batch_types:
#                 raise Exception(_('Invalid Finance Payment Batch Type!'))
#     else:
#         if 'status' in input:
#             statuses = []
#             for export in get_finance_payment_batch_statuses():
#                 statuses.append(export[0])
#
#             if input['status'] not in statuses:
#                 raise Exception(_('Invalid Finance Payment Batch Status!'))
#
#     return result
#
#
# class CreateFinancePaymentBatch(graphene.relay.ClientIDMutation):
#     class Input:
#         name = graphene.String(required=True)
#         batch_type = graphene.String(required=True)
#         finance_payment_batch_category = graphene.ID(required=False)
#         description = graphene.String(required=False)
#         year = graphene.Int(required=False)
#         month = graphene.Int(required=False)
#         execution_date = graphene.types.datetime.Date(required=True)
#         include_zero_amounts = graphene.Boolean(required=False, default_value=False)
#         organization_location = graphene.ID(required=False)
#         note = graphene.String(required=False)
#
#     finance_payment_batch = graphene.Field(FinancePaymentBatchNode)
#
#     @classmethod
#     def mutate_and_get_payload(self, root, info, **input):
#         user = info.context.user
#         require_login_and_permission(user, 'costasiella.add_financepaymentbatch')
#
#         validation_result = validate_create_update_input(input)
#
#         finance_payment_batch = FinancePaymentBatch(
#             name=input['name'],
#             batch_type=input['batch_type'],
#             execution_date=input['execution_date'],
#         )
#
#         if 'include_zero_amounts' in input:
#             finance_payment_batch.include_zero_amounts = input['include_zero_amounts']
#
#         if 'note' in input:
#             finance_payment_batch.note = input['note']
#
#         if 'finance_payment_batch_category' in validation_result:
#             finance_payment_batch.finance_payment_batch_category = validation_result['finance_payment_batch_category']
#
#         if 'organization_location' in validation_result:
#             finance_payment_batch.organization_location = validation_result['organization_location']
#
#         if 'year' in validation_result:
#             finance_payment_batch.year = validation_result['year']
#
#         if 'month' in validation_result:
#             finance_payment_batch.month = validation_result['month']
#
#         finance_payment_batch.save()
#
#         #TODO: Call background task to create batch exports
#
#         return CreateFinancePaymentBatch(finance_payment_batch=finance_payment_batch)
#
#
# class UpdateFinancePaymentBatch(graphene.relay.ClientIDMutation):
#     class Input:
#         id = graphene.ID(required=True)
#         name = graphene.String(required=False)
#         status = graphene.String(required=False)
#         note = graphene.String(required=False)
#
#     finance_payment_batch = graphene.Field(FinancePaymentBatchNode)
#
#     @classmethod
#     def mutate_and_get_payload(self, root, info, **input):
#         user = info.context.user
#         require_login_and_permission(user, 'costasiella.change_financepaymentbatch')
#
#         rid = get_rid(input['id'])
#         finance_payment_batch = FinancePaymentBatch.objects.filter(id=rid.id).first()
#         if not finance_payment_batch:
#             raise Exception('Invalid Finance Payment Batch Category ID!')
#
#         validation_result = validate_create_update_input(input, update=True)
#         finance_payment_batch.name = input['name']
#
#         if 'note' in input:
#             finance_payment_batch.note = input['note']
#
#         if 'status' in validation_result:
#             finance_payment_batch.status = validation_result['status']
#
#         finance_payment_batch.save()
#
#         return UpdateFinancePaymentBatch(finance_payment_batch=finance_payment_batch)
#
#
# class DeleteFinancePaymentBatch(graphene.relay.ClientIDMutation):
#     class Input:
#         id = graphene.ID(required=True)
#
#     ok = graphene.Boolean()
#
#     @classmethod
#     def mutate_and_get_payload(self, root, info, **input):
#         user = info.context.user
#         require_login_and_permission(user, 'costasiella.delete_financepaymentbatch')
#
#         rid = get_rid(input['id'])
#
#         finance_payment_batch = FinancePaymentBatch.objects.filter(id=rid.id).first()
#         if not finance_payment_batch:
#             raise Exception(_('Invalid Finance Payment Batch ID!'))
#
#         ok = finance_payment_batch.delete()
#
#         return DeleteFinancePaymentBatch(ok=ok)
#
#
# class FinancePaymentBatchMutation(graphene.ObjectType):
#     delete_finance_payment_batch = DeleteFinancePaymentBatch.Field()
#     create_finance_payment_batch = CreateFinancePaymentBatch.Field()
#     update_finance_payment_batch = UpdateFinancePaymentBatch.Field()
