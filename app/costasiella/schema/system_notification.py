from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import SystemNotification
from ..modules.gql_tools import require_login_and_permission
from ..modules.messages import Messages

m = Messages()


class SystemNotificationNode(DjangoObjectType):
    class Meta:
        model = SystemNotification
        fields = (
            'name',
            'system_mail_template',
            'accounts'
        )
        filter_fields = {
            'id': ['exact'],
        }
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_systemnotification')

        return self._meta.model.objects.get(id=id)


class SystemNotificationQuery(graphene.ObjectType):
    system_notifications = DjangoFilterConnectionField(SystemNotificationNode)
    system_notification = graphene.relay.Node.Field(SystemNotificationNode)

    @staticmethod
    def resolve_system_notifications(self, info, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_systemnotification')

        # rid = get_rid()
        # return everything:
        return SystemNotification.objects.all().order_by('name')

#
# class UpdateSystemMailTemplate(graphene.relay.ClientIDMutation):
#     class Input:
#         id = graphene.String(required=True)
#         name = graphene.String()
#         system_mail_templa
#
#     system_mail_template = graphene.Field(SystemMailTemplateNode)
#
#     @classmethod
#     def mutate_and_get_payload(self, root, info, **input):
#         user = info.context.user
#         require_login_and_permission(user, 'costasiella.change_systemmailtemplate')
#
#         rid = get_rid(input['id'])
#         system_mail_template = SystemMailTemplate.objects.get(pk=rid.id)
#         if not system_mail_template:
#             raise Exception('Invalid System Mail Template ID!')
#
#         if 'subject' in input:
#             system_mail_template.subject = input['subject']
#
#         if 'title' in input:
#             system_mail_template.title = input['title']
#
#         if 'description' in input:
#             system_mail_template.description = input['description']
#
#         if 'content' in input:
#             system_mail_template.content = input['content']
#
#         if 'comments' in input:
#             system_mail_template.comments = input['comments']
#
#         # Save
#         system_mail_template.save()
#
#         return UpdateSystemMailTemplate(system_mail_template=system_mail_template)
#
#
# class SystemMailTemplateMutation(graphene.ObjectType):
#     update_system_mail_template = UpdateSystemMailTemplate.Field()
