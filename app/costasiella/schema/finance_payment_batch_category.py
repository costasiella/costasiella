from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import FinancePaymentBatchCategory
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class FinancePaymentBatchCategoryNode(DjangoObjectType):
    class Meta:
        model = FinancePaymentBatchCategory
        fields = (
            'archived',
            'name',
            'batch_category_type',
            'description'
        )
        filter_fields = ['archived', 'batch_category_type']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_financepaymentbatchcategory')

        return self._meta.model.objects.get(id=id)


class FinancePaymentBatchCategoryQuery(graphene.ObjectType):
    finance_payment_batch_categories = DjangoFilterConnectionField(FinancePaymentBatchCategoryNode)
    finance_payment_batch_category = graphene.relay.Node.Field(FinancePaymentBatchCategoryNode)

    def resolve_finance_payment_batch_categories(self, info, archived=False, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_financepaymentbatchcategory')

        return FinancePaymentBatchCategory.objects.filter(archived=archived).order_by('-batch_category_type', 'name')


class CreateFinancePaymentBatchCategory(graphene.relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        batch_category_type = graphene.String(required=True)
        description = graphene.String(required=False)

    finance_payment_batch_category = graphene.Field(FinancePaymentBatchCategoryNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_financepaymentbatchcategory')

        finance_payment_batch_category = FinancePaymentBatchCategory(
            name=input['name'],
            batch_category_type=input['batch_category_type']
        )

        if input['description']:
            finance_payment_batch_category.description = input['description']

        finance_payment_batch_category.save()

        return CreateFinancePaymentBatchCategory(finance_payment_batch_category=finance_payment_batch_category)


class UpdateFinancePaymentBatchCategory(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        description = graphene.String(required=False)

    finance_payment_batch_category = graphene.Field(FinancePaymentBatchCategoryNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_financepaymentbatchcategory')

        rid = get_rid(input['id'])

        finance_payment_batch_category = FinancePaymentBatchCategory.objects.filter(id=rid.id).first()
        if not finance_payment_batch_category:
            raise Exception('Invalid Finance Payment Batch Category ID!')

        finance_payment_batch_category.name = input['name']
        if input['description']:
            finance_payment_batch_category.description = input['description']

        finance_payment_batch_category.save()

        return UpdateFinancePaymentBatchCategory(finance_payment_batch_category=finance_payment_batch_category)


class ArchiveFinancePaymentBatchCategory(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    finance_payment_batch_category = graphene.Field(FinancePaymentBatchCategoryNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_financepaymentbatchcategory')

        rid = get_rid(input['id'])

        finance_payment_batch_category = FinancePaymentBatchCategory.objects.filter(id=rid.id).first()
        if not finance_payment_batch_category:
            raise Exception(_('Invalid Finance Payment BatchCategory ID!'))

        finance_payment_batch_category.archived = input['archived']
        finance_payment_batch_category.save()

        return ArchiveFinancePaymentBatchCategory(finance_payment_batch_category=finance_payment_batch_category)


class FinancePaymentBatchCategoryMutation(graphene.ObjectType):
    archive_finance_payment_batch_category = ArchiveFinancePaymentBatchCategory.Field()
    create_finance_payment_batch_category = CreateFinancePaymentBatchCategory.Field()
    update_finance_payment_batch_category = UpdateFinancePaymentBatchCategory.Field()