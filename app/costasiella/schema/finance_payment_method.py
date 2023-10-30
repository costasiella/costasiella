from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import FinancePaymentMethod
from ..modules.gql_tools import require_login, require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class FinancePaymentMethodNode(DjangoObjectType):
    class Meta:
        model = FinancePaymentMethod
        fields = (
            'archived',
            'system_method',
            'name',
            'code'
        )
        filter_fields = ['archived']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login(user)

        finance_payment_method = self._meta.model.objects.get(id=id)

        allowed_pathnames = [
            "AccountSubscriptionNode",
            "FinanceInvoiceNode",
            "FinanceInvoicePaymentNode"
        ]

        # Allow returning data when coming from AccountSubscription
        if info.path.typename in allowed_pathnames:
            return finance_payment_method

        require_login_and_permission(user, 'costasiella.view_financepaymentmethod')

        return finance_payment_method


class FinancePaymentMethodQuery(graphene.ObjectType):
    finance_payment_methods = DjangoFilterConnectionField(FinancePaymentMethodNode)
    finance_payment_method = graphene.relay.Node.Field(FinancePaymentMethodNode)

    def resolve_finance_payment_methods(self, info, archived=False, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_financepaymentmethod')

        ## return everything:
        # if user.has_perm('costasiella.view_financepaymentmethod'):
        return FinancePaymentMethod.objects.filter(archived = archived).order_by('-system_method', 'name')

        # return None


class CreateFinancePaymentMethod(graphene.relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        code = graphene.String(required=False, default_value="")

    finance_payment_method = graphene.Field(FinancePaymentMethodNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_financepaymentmethod')

        errors = []
        if not len(input['name']):
            raise GraphQLError(_('Name is required'))

        finance_payment_method = FinancePaymentMethod(
            name=input['name'], 
        )
        if input['code']:
            finance_payment_method.code = input['code']

        finance_payment_method.save()

        return CreateFinancePaymentMethod(finance_payment_method=finance_payment_method)


class UpdateFinancePaymentMethod(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        code = graphene.String(default_value="")
        
    finance_payment_method = graphene.Field(FinancePaymentMethodNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_financepaymentmethod')

        rid = get_rid(input['id'])

        finance_payment_method = FinancePaymentMethod.objects.filter(id=rid.id).first()
        if not finance_payment_method:
            raise Exception('Invalid Finance Payment Method ID!')

        finance_payment_method.name = input['name']
        if input['code']:
            finance_payment_method.code = input['code']

        finance_payment_method.save(force_update=True)

        return UpdateFinancePaymentMethod(finance_payment_method=finance_payment_method)


class ArchiveFinancePaymentMethod(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    finance_payment_method = graphene.Field(FinancePaymentMethodNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_financepaymentmethod')

        rid = get_rid(input['id'])

        finance_payment_method = FinancePaymentMethod.objects.filter(id=rid.id).first()
        if not finance_payment_method:
            raise Exception(_('Invalid Finance Payment Method ID!'))

        if finance_payment_method.system_method:
            raise Exception(_('Unable to archive, this is a system method!'))

        finance_payment_method.archived = input['archived']
        finance_payment_method.save()

        return ArchiveFinancePaymentMethod(finance_payment_method=finance_payment_method)


class FinancePaymentMethodMutation(graphene.ObjectType):
    archive_finance_payment_method = ArchiveFinancePaymentMethod.Field()
    create_finance_payment_method = CreateFinancePaymentMethod.Field()
    update_finance_payment_method = UpdateFinancePaymentMethod.Field()