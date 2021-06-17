from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import SystemFeatureShop
from ..modules.gql_tools import require_login, require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class SystemFeatureShopNode(DjangoObjectType):   
    class Meta:
        model = SystemFeatureShop
        filter_fields = {
            'setting': ['exact'],
        }
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_systemfeatureshop')

        return self._meta.model.objects.get(id=id)


class SystemFeatureShopQuery(graphene.ObjectType):
    system_feature_shop = graphene.relay.Node.Field(SystemFeatureShopNode)

    # def resolve_system_settings(self, info, **kwargs):
    #     user = info.context.user
    #     require_login_and_permission(user, 'costasiella.view_systemfeatureshop')
    #
    #     return SystemSetting.objects.all()


class UpdateSystemFeatureShop(graphene.relay.ClientIDMutation):
    class Input:
        memberships = graphene.Boolean(required=False)
        subscriptions = graphene.Boolean(required=False)
        classpasses = graphene.Boolean(required=False)
        classes = graphene.Boolean(required=False)
        events = graphene.Boolean(required=False)
        
    system_feature_shop = graphene.Field(SystemFeatureShopNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_systemfeatureshop')

        system_feature_shop = SystemFeatureShop.objects.get(id=1)

        if 'memberships' in input:
            system_feature_shop.memberships = input['memberships']

        if 'subscriptions' in input:
            system_feature_shop.subscriptions = input['subscriptions']

        if 'classpasses' in input:
            system_feature_shop.classpasses = input['classpasses']

        if 'classes' in input:
            system_feature_shop.classes = input['classes']

        if 'events' in input:
            system_feature_shop.events = input['events']

        # Save
        system_feature_shop.save()

        return UpdateSystemFeatureShop(system_feature_shop=system_feature_shop)


class SystemFeatureShopMutation(graphene.ObjectType):
    update_system_feature_shop = UpdateSystemFeatureShop.Field()
