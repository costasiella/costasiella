from django.utils.translation import gettext as _

import validators
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import FinanceTaxRate
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class FinanceTaxRateNode(DjangoObjectType):
    class Meta:
        model = FinanceTaxRate
        filter_fields = ['archived']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_financetaxrate')

        return self._meta.model.objects.get(id=id)


class FinanceTaxRateQuery(graphene.ObjectType):
    finance_taxrates = DjangoFilterConnectionField(FinanceTaxRateNode)
    finance_taxrate = graphene.relay.Node.Field(FinanceTaxRateNode)

    def resolve_finance_taxrates(self, info, archived=False, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_financetaxrate')

        ## return everything:
        # if user.has_perm('costasiella.view_financetaxrate'):
        return FinanceTaxRate.objects.filter(archived = archived).order_by('name')


class CreateFinanceTaxRate(graphene.relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        percentage = graphene.Int(required=True)
        rateType = graphene.String(required=True)
        code = graphene.String(required=False, default_value="")

    finance_taxrate = graphene.Field(FinanceTaxRateNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_financetaxrate')

        errors = []
        if not len(input['name']):
            print('validation error found')
            raise GraphQLError(_('Name is required'))

        # if not input['percentage'] and not input['percentage'] == 0:
        #     raise GraphQLError(_('Percentage is required'))

        if not validators.between(input['percentage'], 0, 100):
            raise GraphQLError(_('Percentage has to be between 0 and 100'))

        finance_taxrate = FinanceTaxRate(
            name=input['name'], 
            percentage=input['percentage'],
            rate_type=input['rateType']
        )
        if input['code']:
            finance_taxrate.code = input['code']

        finance_taxrate.save()

        return CreateFinanceTaxRate(finance_taxrate=finance_taxrate)


class UpdateFinanceTaxRate(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        percentage = graphene.Int(required=True)
        rateType = graphene.String(required=True)
        code = graphene.String(default_value="")
        
    finance_taxrate = graphene.Field(FinanceTaxRateNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_financetaxrate')

        rid = get_rid(input['id'])

        finance_taxrate = FinanceTaxRate.objects.filter(id=rid.id).first()
        if not finance_taxrate:
            raise Exception('Invalid Finance Tax Rate ID!')

        if not validators.between(input['percentage'], 0, 100):
            raise GraphQLError(_('Percentage has to be between 0 and 100'))

        finance_taxrate.name = input['name']
        finance_taxrate.percentage = input['percentage']
        finance_taxrate.rate_type = input['rateType']
        if input['code']:
            finance_taxrate.code = input['code']
        finance_taxrate.save(force_update=True)

        return UpdateFinanceTaxRate(finance_taxrate=finance_taxrate)


class ArchiveFinanceTaxRate(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    finance_taxrate = graphene.Field(FinanceTaxRateNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_financetaxrate')

        rid = get_rid(input['id'])

        finance_taxrate = FinanceTaxRate.objects.filter(id=rid.id).first()
        if not finance_taxrate:
            raise Exception('Invalid Finance Tax Rate ID!')

        finance_taxrate.archived = input['archived']
        finance_taxrate.save(force_update=True)

        return ArchiveFinanceTaxRate(finance_taxrate=finance_taxrate)


class FinanceTaxRateMutation(graphene.ObjectType):
    archive_finance_taxrate = ArchiveFinanceTaxRate.Field()
    create_finance_taxrate = CreateFinanceTaxRate.Field()
    update_finance_taxrate = UpdateFinanceTaxRate.Field()