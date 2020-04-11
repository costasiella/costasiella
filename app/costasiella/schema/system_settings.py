from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import SystemSetting
from ..modules.gql_tools import require_login, require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class SystemSettingNode(DjangoObjectType):   
    class Meta:
        model = SystemSetting
        filter_fields = ['setting']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_systemsetting')

        return self._meta.model.objects.get(id=id)


class SystemSettingQuery(graphene.ObjectType):
    system_settings = DjangoFilterConnectionField(SystemSettingNode)
    system_setting = graphene.relay.Node.Field(SystemSettingNode)


    def resolve_system_settings(self, info, account, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_system_settings')

        rid = get_rid(account)

        ## return everything:
        return SystemSetting.objects.all()


class UpdateSystemSetting(graphene.relay.ClientIDMutation):
    class Input:
        setting = graphene.String(required=True)
        value = graphene.String(required=True, default="")
        
    system_setting = graphene.Field(SystemSettingNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_systemsetting')

        system_setting = SystemSetting.objects.get(setting=setting)
        if not system_setting:
            # Insert
            system_setting = SystemSetting(
                setting = input['setting']
                value = input['value']
            )
        else:
            # Update
            system_setting.setting = input['setting']
            system_setting.value = input['value']

        # Save
        system_setting.save()

        return UpdateSystemSetting(system_setting=system_setting)


class SystemSettingMutation(graphene.ObjectType):
    update_system_setting = UpdateSystemSetting.Field()
