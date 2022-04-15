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
        fields = (
            'setting',
            'value'
        )
        filter_fields = {
            'setting': ['exact'],
        }
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_systemsetting')

        id = kwargs.get('id')
        setting = kwargs.get('name')

        if id:
            return self._meta.model.objects.get(id=id)
        if setting:
            return self._meta.model.objects.get(setting=setting)


class SystemSettingQuery(graphene.ObjectType):
    system_settings = DjangoFilterConnectionField(SystemSettingNode)
    system_setting = graphene.relay.Node.Field(SystemSettingNode)

    def resolve_system_settings(self, info, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_systemsetting')

        return SystemSetting.objects.all()


def validate_update_input(input):
    """
    Validate input for settings that can only be set to specific values
    """
    if input['setting'] == 'workflow_shop_subscription_payment_method':
        valid_payment_methods = [
            'DIRECTDEBIT',
            'MOLLIE'
        ]
        if input['value'] not in valid_payment_methods:
            raise Exception(_("Valid payment methods are 'DIRECTDEBIT' and 'MOLLIE'"))


class UpdateSystemSetting(graphene.relay.ClientIDMutation):
    class Input:
        setting = graphene.String(required=True)
        value = graphene.String(required=True, default="")
        
    system_setting = graphene.Field(SystemSettingNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_systemsetting')

        validate_update_input(input)

        qs = SystemSetting.objects.filter(setting=input['setting'])
        if not qs.exists():
            # Insert
            system_setting = SystemSetting(
                setting = input['setting'],
                value = input['value']
            )
        else:
            # Update
            system_setting = qs.first()
            system_setting.setting = input['setting']
            system_setting.value = input['value']

        # Save
        system_setting.save()

        return UpdateSystemSetting(system_setting=system_setting)


class SystemSettingMutation(graphene.ObjectType):
    update_system_setting = UpdateSystemSetting.Field()
