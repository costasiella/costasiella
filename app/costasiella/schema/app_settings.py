from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from django.conf import settings

from ..models import AppSettings, SystemSetting
from ..modules.gql_tools import require_login, require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class AppSettingsNodeInterface(graphene.Interface):
    time_format_moment = graphene.String()
    date_time_format_moment = graphene.String()
    online_payments_available = graphene.Boolean()
    account_signup_enabled = graphene.Boolean()


class AppSettingsNode(DjangoObjectType):
    # Prevent formats from changing (all uppercase or dashes changed to underscores in formats)
    # More info here:
    # http://docs.graphene-python.org/en/latest/types/schema/#auto-camelcase-field-names
    date_format = graphene.Field(graphene.String, source='date_format')
    time_format = graphene.Field(graphene.String, source='time_format')

    class Meta:
        model = AppSettings
        fields = (
            'date_format',
            'time_format'
        )
        interfaces = (graphene.relay.Node, AppSettingsNodeInterface,)

    def resolve_time_format_moment(self, info):
        if self.time_format == "24":
            return "HH:mm"
        else:
            return "hh:mm a"

    def resolve_date_time_format_moment(self, info):
        if self.time_format == "24":
            time_format_moment = "HH:mm"
        else:
            time_format_moment = "hh:mm a"

        return self.date_format + " " + time_format_moment

    def resolve_online_payments_available(self, info):
        """
        Check if online payments are available by checking if a payment provider API key is present
        """
        mollie_configured = False
        qs = SystemSetting.objects.filter(setting='integration_mollie_api_key')
        if qs.exists():
            system_setting = qs.first()
            if system_setting.value:
                mollie_configured = True

        return mollie_configured

    def resolve_account_signup_enabled(self, info):
        """
        Check if account sign up is open or closed
        :param info:
        :return:
        """
        signup_enabled = True

        try:
            if settings.ACCOUNT_ADAPTER == \
                    'costasiella.allauth_adapters.account_adapter_no_signup.AccountAdapterNoSignup':
                signup_enabled = False
        except AttributeError:
            # settings.ACCOUNT_ADAPTER is not set and the default values are used
            pass

        return signup_enabled

    @classmethod
    def get_node(self, info, id):
        # user = info.context.user
        # require_login(user)

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
