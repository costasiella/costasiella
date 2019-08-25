from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import AppSettings
from ..modules.gql_tools import require_login, get_rid
from ..modules.messages import Messages

m = Messages()


class AppSettingsNode(DjangoObjectType):
    # Prevent formats from changing (all uppercase or dashes changed to underscores in formats)
    # More info here:
    # http://docs.graphene-python.org/en/latest/types/schema/#auto-camelcase-field-names
    
    date_format = graphene.Field(graphene.String, source='date_format')
    time_format = graphene.Field(graphene.String, source='time_format')

    class Meta:
        model = AppSettings
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login(user)

        return self._meta.model.objects.get(id=id)


class AppSettingsQuery(graphene.ObjectType):
    app_settings = graphene.relay.Node.Field(AppSettingsNode)


class UpdateAppSettings(graphene.relay.ClientIDMutation):
    class Input:
        date_format = graphene.String(required=False)
        time_format = graphene.String(required=False)
        
    app_settings = graphene.Field(AppSettingsNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_appsettings')

        app_settings = AppSettings.objects.get(id=1)

        if 'date_format' in input:
            app_settings.date_format = input['date_format']

        if 'time_format' in input:
            app_settings.time_format = input['time_format']


        app_settings.save()

        return UpdateAppSettings(app_settings=app_settings)


class AppSettingsMutation(graphene.ObjectType):
    update_app_settings = UpdateAppSettings.Field()
