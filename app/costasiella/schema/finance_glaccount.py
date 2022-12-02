from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import FinanceGLAccount
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class FinanceGLAccountNode(DjangoObjectType):
    class Meta:
        model = FinanceGLAccount
        fields = (
            'archived',
            'name',
            'code'
        )
        filter_fields = ['archived']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_financeglaccount')

        return self._meta.model.objects.get(id=id)


class FinanceGLAccountQuery(graphene.ObjectType):
    finance_glaccounts = DjangoFilterConnectionField(FinanceGLAccountNode)
    finance_glaccount = graphene.relay.Node.Field(FinanceGLAccountNode)

    def resolve_finance_glaccounts(self, info, archived=False, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_financeglaccount')

        ## return everything:
        # if user.has_perm('costasiella.view_financeglaccount'):
        return FinanceGLAccount.objects.filter(archived = archived).order_by('code')

        # return None


class CreateFinanceGLAccount(graphene.relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        code = graphene.Int(required=False)

    finance_glaccount = graphene.Field(FinanceGLAccountNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_financeglaccount')

        finance_glaccount = FinanceGLAccount(
            name=input['name'], 
        )

        if input['code']:
            finance_glaccount.code = input['code']

        finance_glaccount.save()

        return CreateFinanceGLAccount(finance_glaccount=finance_glaccount)


class UpdateFinanceGLAccount(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        code = graphene.Int(required=False)
        
    finance_glaccount = graphene.Field(FinanceGLAccountNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_financeglaccount')

        rid = get_rid(input['id'])

        finance_glaccount = FinanceGLAccount.objects.filter(id=rid.id).first()
        if not finance_glaccount:
            raise Exception('Invalid Finance GLAccount ID!')

        finance_glaccount.name = input['name']
        if input['code']:
            finance_glaccount.code = input['code']

        finance_glaccount.save()

        return UpdateFinanceGLAccount(finance_glaccount=finance_glaccount)


class ArchiveFinanceGLAccount(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    finance_glaccount = graphene.Field(FinanceGLAccountNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_financeglaccount')

        rid = get_rid(input['id'])

        finance_glaccount = FinanceGLAccount.objects.filter(id=rid.id).first()
        if not finance_glaccount:
            raise Exception('Invalid Finance GLAccount ID!')

        finance_glaccount.archived = input['archived']
        finance_glaccount.save()

        return ArchiveFinanceGLAccount(finance_glaccount=finance_glaccount)


class FinanceGLAccountMutation(graphene.ObjectType):
    archive_finance_glaccount = ArchiveFinanceGLAccount.Field()
    create_finance_glaccount = CreateFinanceGLAccount.Field()
    update_finance_glaccount = UpdateFinanceGLAccount.Field()