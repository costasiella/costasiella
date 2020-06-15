from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import Account, ScheduleItem, ScheduleItemMail
from ..modules.gql_tools import require_login, require_login_and_permission, \
                                require_login_and_one_of_permissions, get_rid
from ..modules.messages import Messages
from ..models.choices.schedule_item_frequency_types import get_schedule_item_frequency_types

from ..dudes import ClassCheckinDude, ClassScheduleDude

m = Messages()


class ScheduleItemMailNode(DjangoObjectType):
    class Meta:
        model = ScheduleItemMail
        filter_fields = ['schedule_item', 'frequency_type', 'date']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_one_of_permissions(user, [
            'costasiella.view_scheduleitemmail',
        ])

        # Return only public non-archived location rooms
        return self._meta.model.objects.get(id=id)


class ScheduleItemMailQuery(graphene.ObjectType):
    schedule_item_mails = DjangoFilterConnectionField(ScheduleItemMailNode)
    schedule_item_mail = graphene.relay.Node.Field(ScheduleItemMailNode)

    def resolve_schedule_item_mails(self, info, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_scheduleitemmail')

        return ScheduleItemMail.objects.all()
            

def validate_schedule_item_mail_create_update_input(input):
    """
    Validate input
    """ 
    result = {}

    # check frequency_type
    if 'frequency_type' in input:
        valid_frequency_type = False
        frequency_types = get_schedule_item_frequency_types()
        for t in frequency_types:
            if input['frequency_type'] == t[0]:
                valid_frequency_type = True
                break
        if not valid_frequency_type:
            raise Exception(_('Invalid frequency type!'))
        elif input['frequency_type'] == "SPECIFIC":
            if 'date' not in input:
                raise Exception(_("Date is required when setting frequency type to specific!"))

    # Check Schedule Item
    if 'schedule_item' in input:
        if input['schedule_item']:
            rid = get_rid(input['schedule_item'])
            schedule_item = ScheduleItem.objects.get(id=rid.id)
            result['schedule_item'] = schedule_item
            if not schedule_item:
                raise Exception(_('Invalid Schedule Item (class) ID!'))

    return result


class CreateScheduleItemMail(graphene.relay.ClientIDMutation):
    class Input:
        schedule_item = graphene.ID(required=True)
        frequency_type = graphene.String(required=True)
        date = graphene.types.datetime.Date(required=False)
        mail_content = graphene.String(required=True)

    schedule_item_mail = graphene.Field(ScheduleItemMailNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_scheduleitemmail')

        validation_result = validate_schedule_item_mail_create_update_input(input)

        schedule_item_mail = ScheduleItemMail.create(
            schedule_item=validation_result['schedule_item'],
            frequency_type=input['frequency_type'],
            date=input.get('date', None)
        )
        schedule_item_mail.save()

        return CreateScheduleItemMail(schedule_item_mail=schedule_item_mail)


class UpdateScheduleItemMail(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        mail_content = graphene.String(required=True)
        
    schedule_item_mail = graphene.Field(ScheduleItemMailNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_scheduleitemmail')

        rid = get_rid(input['id'])
        schedule_item_mail = ScheduleItemMail.objects.filter(id=rid.id).first()
        if not schedule_item_mail:
            raise Exception('Invalid Schedule Item Mail ID!')

        schedule_item_mail.mail_content = input['mail_content']
        schedule_item_mail.save()

        return UpdateScheduleItemMail(schedule_item_mail=schedule_item_mail)


class DeleteScheduleItemMail(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_scheduleitemmail')

        rid = get_rid(input['id'])
        schedule_item_mail = ScheduleItemMail.objects.filter(id=rid.id).first()
        if not schedule_item_mail:
            raise Exception('Invalid Schedule Item Mail ID!')

        # Actually remove
        ok = schedule_item_mail.delete()

        return DeleteScheduleItemMail(ok=ok)


class ScheduleItemMailMutation(graphene.ObjectType):
    delete_schedule_item_mail = DeleteScheduleItemMail.Field()
    create_schedule_item_mail = CreateScheduleItemMail.Field()
    update_schedule_item_mail = UpdateScheduleItemMail.Field()