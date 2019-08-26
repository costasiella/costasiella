from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import ScheduleItem, ScheduleItemWeeklyOTC, OrganizationClasstype, OrganizationLocationRoom, OrganizationLevel
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

from ..dudes import ClassScheduleDude

m = Messages()

class ScheduleClassWeeklyOTCNode(DjangoObjectType):
    class Meta:
        model = ScheduleItemWeeklyOTC
        filter_fields = ['schedule_item', 'date']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_scheduleclassweeklyotc')

        return self._meta.model.objects.get(id=id)


class ScheduleClassWeeklyOTCQuery(graphene.ObjectType):
    schedule_class_weekly_otcs = DjangoFilterConnectionField(ScheduleClassWeeklyOTCNode)
    schedule_class_weekly_otc = graphene.relay.Node.Field(ScheduleClassWeeklyOTCNode)

    def resolve_schedule_class_weekly_otcs(self, info, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_scheduleclassweeklyotc')

        return ScheduleItemWeeklyOTC.objects.all()
            

def validate_update_input(input):
    """
    Validate input
    """ 
    result = {}

    # Check ScheduleItem
    rid = get_rid(input['schedule_item'])
    schedule_item = ScheduleItem.objects.get(id=rid.id)
    result['schedule_item'] = schedule_item
    if not schedule_item:
        raise Exception(_('Invalid Schedule Item ID!'))    

    # Check date
    class_schedule_dude = ClassScheduleDude()
    class_takes_place = class_schedule_dude.schedule_item_takes_place_on_day(
        schedule_item = schedule_item,
        date = input['date']
    )
    
    if not class_takes_place:
        raise Exception(_("This class doesn't take place on this date, please check for the correct date or any holidays."))
    
    # Check OrganizationLocationRoom
    if 'organization_location_room' in input:
        if input['organization_location_room']:
            rid = get_rid(input['organization_location_room'])
            organization_location_room = OrganizationLocationRoom.objects.filter(id=rid.id).first()
            result['organization_location_room'] = organization_location_room
            if not organization_location_room:
                raise Exception(_('Invalid Organization Location Room ID!'))            

    # Check OrganizationClasstype
    if 'organization_classtype' in input:
        if input['organization_classtype']:
            rid = get_rid(input['organization_classtype'])
            organization_classtype = OrganizationClasstype.objects.get(id=rid.id)
            result['organization_classtype'] = organization_classtype
            if not organization_classtype:
                raise Exception(_('Invalid Organization Classtype ID!'))            

    # Check OrganizationLevel
    if 'organization_level' in input:
        if input['organization_level']:
            print('processing')
            rid = get_rid(input['organization_level'])
            organization_level = OrganizationLevel.objects.get(id=rid.id)
            result['organization_level'] = organization_level
            if not organization_level:
                raise Exception(_('Invalid Organization Level ID!'))            


    return result


# class CreateScheduleClassWeeklyOTC(graphene.relay.ClientIDMutation):
#     class Input:
#         schedule_item = graphene.ID(required=True)
#         date = graphene.types.datetime.Date(required=True)
#         organization_location_room = graphene.ID(required=False)
#         organization_classtype = graphene.ID(required=False)
#         organization_level = graphene.ID(required=False)        
#         time_start = graphene.types.datetime.Time(required=False)
#         time_end = graphene.types.datetime.Time(required=False)

#     schedule_class_weekly_otc = graphene.Field(ScheduleClassWeeklyOTCNode)

#     @classmethod
#     def mutate_and_get_payload(self, root, info, **input):
#         user = info.context.user
#         require_login_and_permission(user, 'costasiella.add_scheduleclassweeklyotc')

#         result = validate_create_update_input(input)

#         print(input)

#         schedule_class_weekly_otc = ScheduleItemWeeklyOTC(
#             schedule_item = result['schedule_item'],
#             date = input['date'],
#         )

#         if 'organization_location_room' in result:
#             schedule_class_weekly_otc.organization_location_room = result['organization_location_room']

#         if 'organization_classtype' in result:
#             schedule_class_weekly_otc.organization_classtype = result['organization_classtype']

#         if 'organization_level' in result:
#             schedule_class_weekly_otc.organization_level = result['organization_level']

#         if 'time_start' in input:
#             schedule_class_weekly_otc.time_start = input['time_start']

#         if 'time_end' in input:
#             schedule_class_weekly_otc.time_end = input['time_end']


#         # ALl done, save it :).
#         schedule_class_weekly_otc.save()

#         return CreateScheduleClassWeeklyOTC(schedule_class_weekly_otc=schedule_class_weekly_otc)


class UpdateScheduleClassWeeklyOTC(graphene.relay.ClientIDMutation):
    class Input:
        schedule_item = graphene.ID(required=True)
        date = graphene.types.datetime.Date(required=True)
        organization_location_room = graphene.ID(required=False)
        organization_classtype = graphene.ID(required=False)
        organization_level = graphene.ID(required=False)        
        time_start = graphene.types.datetime.Time(required=False)
        time_end = graphene.types.datetime.Time(required=False)
        
    schedule_class_weekly_otc = graphene.Field(ScheduleClassWeeklyOTCNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_scheduleclassweeklyotc')

        result = validate_update_input(input)

        # rid = get_rid(input['id'])
        qs = ScheduleItemWeeklyOTC.objects.filter(
            schedule_item = result['schedule_item'],
            date = input['date']
        )
        if qs.exists:
            # Update
            schedule_class_weekly_otc = qs.first()
        else:
            # Insert if it doesn't exist
            schedule_class_weekly_otc = ScheduleItemWeeklyOTC(
                schedule_item = result['schedule_item'],
                date = input['date']
            )

        
        
        if 'organization_location_room' in result:
            schedule_class_weekly_otc.organization_location_room = result['organization_location_room']

        if 'organization_classtype' in result:
            schedule_class_weekly_otc.organization_classtype = result['organization_classtype']

        if 'organization_level' in result:
            schedule_class_weekly_otc.organization_level = result['organization_level']

        if 'time_start' in input:
            schedule_class_weekly_otc.time_start = input['time_start']

        if 'time_end' in input:
            schedule_class_weekly_otc.time_end = input['time_end']

        schedule_class_weekly_otc.save()

        return UpdateScheduleClassWeeklyOTC(schedule_class_weekly_otc=schedule_class_weekly_otc)


class DeleteScheduleClassWeeklyOTC(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_scheduleclassweeklyotc')

        rid = get_rid(input['id'])
        schedule_class_weekly_otc = ScheduleItemWeeklyOTC.objects.filter(id=rid.id).first()
        if not schedule_class_weekly_otc:
            raise Exception('Invalid Schedule Class Attendance ID!')

        # Actually remove
        ok = schedule_class_weekly_otc.delete()

        return DeleteScheduleClassWeeklyOTC(ok=ok)


class ScheduleClassWeeklyOTCMutation(graphene.ObjectType):
    delete_schedule_class_weekly_otc = DeleteScheduleClassWeeklyOTC.Field()
    # create_schedule_class_weekly_otc = CreateScheduleClassWeeklyOTC.Field()
    update_schedule_class_weekly_otc = UpdateScheduleClassWeeklyOTC.Field()
    