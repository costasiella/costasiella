from django.utils.translation import gettext as _

import datetime
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

import validators

from ..dudes import SystemSettingDude
from ..models import AccountSubscription, AccountSubscriptionPause
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

from sorl.thumbnail import get_thumbnail

m = Messages()


def validate_create_update_input(input, update=False):
    """
    Validate input
    """
    system_setting_dude = SystemSettingDude()
    result = {}

    if input['date_start'] > input['date_end']:
        raise Exception(_("End date should be bigger than start date"))

    # Check min. duration
    min_pause_duration = system_setting_dude.get("workflow_subscription_pauses_min_duration_in_days") or 1
    min_pause_duration = int(min_pause_duration)
    delta = input['date_end'] - input['date_start']
    if delta.days + 1 < min_pause_duration:
        raise Exception(_("A pause should be at least %s day(s)") % min_pause_duration)

    if not update:
        # Fetch & check account subscription
        rid = get_rid(input['account_subscription'])
        account_subscription = AccountSubscription.objects.get(pk=rid.id)
        result['account_subscription'] = account_subscription
        if not account_subscription:
            raise Exception(_('Invalid Account Subscription ID!'))

        # Check if the maximum number of pauses hasn't been reached
        max_pauses = system_setting_dude.get("workflow_subscription_pauses_max_pauses_in_year") or 1
        max_pauses = int(max_pauses)
        start_of_year = datetime.date(input['date_start'].year, 1, 1)
        end_of_year = datetime.date(input['date_start'].year, 12, 31)
        qs = AccountSubscriptionPause.objects.filter(
            account_subscription=account_subscription,
            date_start__gte=start_of_year,
            date_start__lte=end_of_year
        )
        pauses_in_year = qs.count()

        if pauses_in_year >= max_pauses:
            raise Exception(_("Maximum number of pauses reached for year %s") % input['date_start'].year)

    return result


class AccountSubscriptionPauseNode(DjangoObjectType):
    class Meta:
        model = AccountSubscriptionPause
        # Fields to include
        fields = (
            'account_subscription',
            'date_start',
            'date_end',
            'description',
            'created_at',
            'updated_at'
        )
        filter_fields = {
            'account_subscription': ['exact'],
        }
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_accountsubscriptionpause')

        return self._meta.model.objects.get(id=id)


class AccountSubscriptionPauseQuery(graphene.ObjectType):
    account_subscription_pauses = DjangoFilterConnectionField(AccountSubscriptionPauseNode)
    account_subscription_pause = graphene.relay.Node.Field(AccountSubscriptionPauseNode)

    def resolve_account_subscription_pauses(self, info, account_subscription, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_accountsubscriptionpause')
        rid = get_rid(account_subscription)

        # return everything:
        return AccountSubscriptionPause.objects.filter(account_subscription__id=rid.id).order_by('-date_start')


class CreateAccountSubscriptionPause(graphene.relay.ClientIDMutation):
    class Input:
        account_subscription = graphene.ID(required=True)
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=True)
        description = graphene.String(required=False, default_value="")

    account_subscription_pause = graphene.Field(AccountSubscriptionPauseNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_accountsubscriptionpause')

        # Validate input
        result = validate_create_update_input(input, update=False)

        account_subscription_pause = AccountSubscriptionPause(
            account_subscription=result['account_subscription'],
            date_start=input['date_start'],
            date_end=input['date_end'],
            description=input['description']
        )

        account_subscription_pause.save()
        account_subscription_pause.cancel_booked_classes_during_pause()

        return CreateAccountSubscriptionPause(account_subscription_pause=account_subscription_pause)


class UpdateAccountSubscriptionPause(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=True)
        description = graphene.String(required=False, default_value="")
        
    account_subscription_pause = graphene.Field(AccountSubscriptionPauseNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_accountsubscriptionpause')

        rid = get_rid(input['id'])
        account_subscription_pause = AccountSubscriptionPause.objects.filter(id=rid.id).first()
        if not account_subscription_pause:
            raise Exception('Invalid Account Subscription Pause ID!')

        result = validate_create_update_input(input, update=True)

        account_subscription_pause.date_start = input['date_start']
        account_subscription_pause.date_end = input['date_end']
        account_subscription_pause.description = input['description']

        account_subscription_pause.save()

        return UpdateAccountSubscriptionPause(account_subscription_pause=account_subscription_pause)


class DeleteAccountSubscriptionPause(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_accountsubscriptionpause')

        rid = get_rid(input['id'])
        account_subscription_pause = AccountSubscriptionPause.objects.filter(id=rid.id).first()
        if not account_subscription_pause:
            raise Exception('Invalid Account Subscription Pause ID!')

        ok = bool(account_subscription_pause.delete())

        return DeleteAccountSubscriptionPause(ok=ok)


class AccountSubscriptionPauseMutation(graphene.ObjectType):
    create_account_subscription_pause = CreateAccountSubscriptionPause.Field()
    delete_account_subscription_pause = DeleteAccountSubscriptionPause.Field()
    update_account_subscription_pause = UpdateAccountSubscriptionPause.Field()
