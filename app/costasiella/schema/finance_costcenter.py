from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import FinanceCostCenter
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class FinanceCostCenterNode(DjangoObjectType):
    class Meta:
        model = FinanceCostCenter
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
        require_login_and_permission(user, 'costasiella.view_financecostcenter')

        return self._meta.model.objects.get(id=id)


class FinanceCostCenterQuery(graphene.ObjectType):
    finance_costcenters = DjangoFilterConnectionField(FinanceCostCenterNode)
    finance_costcenter = graphene.relay.Node.Field(FinanceCostCenterNode)

    def resolve_finance_costcenters(self, info, archived=False, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_financecostcenter')

        ## return everything:
        # if user.has_perm('costasiella.view_financecostcenter'):
        return FinanceCostCenter.objects.filter(archived = archived).order_by('code')

        # return None


class CreateFinanceCostCenter(graphene.relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        code = graphene.Int(required=False)

    finance_costcenter = graphene.Field(FinanceCostCenterNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_financecostcenter')

        finance_costcenter = FinanceCostCenter(
            name=input['name'], 
        )

        if input['code']:
            finance_costcenter.code = input['code']

        finance_costcenter.save()

        return CreateFinanceCostCenter(finance_costcenter=finance_costcenter)


class UpdateFinanceCostCenter(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        code = graphene.Int(required=False)
        
    finance_costcenter = graphene.Field(FinanceCostCenterNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_financecostcenter')

        rid = get_rid(input['id'])
        finance_costcenter = FinanceCostCenter.objects.filter(id=rid.id).first()
        if not finance_costcenter:
            raise Exception('Invalid Finance Costcenter ID!')

        finance_costcenter.name = input['name']
        if input['code']:
            finance_costcenter.code = input['code']

        finance_costcenter.save()

        return UpdateFinanceCostCenter(finance_costcenter=finance_costcenter)


class ArchiveFinanceCostCenter(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    finance_costcenter = graphene.Field(FinanceCostCenterNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_financecostcenter')

        rid = get_rid(input['id'])

        finance_costcenter = FinanceCostCenter.objects.filter(id=rid.id).first()
        if not finance_costcenter:
            raise Exception('Invalid Finance Costcenter ID!')

        finance_costcenter.archived = input['archived']
        finance_costcenter.save()

        return ArchiveFinanceCostCenter(finance_costcenter=finance_costcenter)


class FinanceCostCenterMutation(graphene.ObjectType):
    archive_finance_costcenter = ArchiveFinanceCostCenter.Field()
    create_finance_costcenter = CreateFinanceCostCenter.Field()
    update_finance_costcenter = UpdateFinanceCostCenter.Field()
