from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import SystemMailTemplate
from ..modules.gql_tools import require_login, require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class SystemMailTemplateNode(DjangoObjectType):
    class Meta:
        model = SystemMailTemplate
        filter_fields = {
            'id': ['exact'],
        }
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_systemmailtemplate')

        print(kwargs)
        id = kwargs.get('id')

        return self._meta.model.objects.get(id=id)


class SystemMailTemplateQuery(graphene.ObjectType):
    system_mail_templates = DjangoFilterConnectionField(SystemMailTemplateNode)
    system_mail_template = graphene.relay.Node.Field(SystemMailTemplateNode)

    def resolve_mail_templates(self, info, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_systemmailtemplate')

        # rid = get_rid()
        # return everything:
        return SystemMailTemplate.objects.all()


class UpdateSystemSetting(graphene.relay.ClientIDMutation):
    class Input:
        subject = graphene.String()
        title = graphene.String()
        description = graphene.String()
        content = graphene.String()
        comments = graphene.String()
        
    system_setting = graphene.Field(SystemMailTemplateNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_systemsetting')

        record_found = SystemSetting.objects.filter(setting=input['setting']).exists()
        if not record_found:
            # Insert
            system_setting = SystemSetting(
                setting = input['setting'],
                value = input['value']
            )
        else:
            # Update
            system_setting = SystemSetting.objects.filter(setting=input['setting']).first()
            system_setting.setting = input['setting']
            system_setting.value = input['value']

        # Save
        system_setting.save()

        return UpdateSystemSetting(system_setting=system_setting)


class SystemSettingMutation(graphene.ObjectType):
    update_system_setting = UpdateSystemSetting.Field()
