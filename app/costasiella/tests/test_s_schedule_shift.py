# from graphql.error.located_error import GraphQLLocatedError
import graphql
import base64
import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from graphene.test import Client
from graphql_relay import to_global_id

# Create your tests here.
from django.contrib.auth.models import AnonymousUser, Permission

from . import factories as f
from .helpers import execute_test_client_api_query
from .. import models
from .. import schema
from ..modules.gql_tools import get_rid

from .tools import next_weekday


class GQLScheduleClass(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_scheduleshift'
        self.permission_add = 'add_scheduleshift'
        self.permission_change = 'change_scheduleshift'
        self.permission_delete = 'delete_scheduleshift'

        a_monday = datetime.date(2021, 12, 27)
        self.variables_query_list = {
            'dateFrom': str(a_monday),
            'dateUntil': str(a_monday + datetime.timedelta(days=6)),
        }

        status_monday = datetime.date(2030, 12, 30)
        self.variables_query_list_status = {
            'dateFrom': str(status_monday),
            'dateUntil': str(status_monday + datetime.timedelta(days=6)),
        }

        self.organization_location_room = f.OrganizationLocationRoomFactory.create()
        self.organization_shift = f.OrganizationShiftFactory.create()
        
        # self.variables_create = {
        #     "input": {
        #         "frequencyType": "WEEKLY",
        #         "frequencyInterval": 1, # Monday,
        #         "organizationLocationRoom": to_global_id('OrganizationLocationRoomNode', self.organization_location_room.id),
        #         "organizationClasstype": to_global_id('OrganizationClasstypeNode', self.organization_classtype.id),
        #         "organizationLevel": to_global_id('OrganizationLevelNode', self.organization_level.id),
        #         "dateStart": "2019-01-01",
        #         "dateEnd": "2999-12-31",
        #         "timeStart": "11:00:00",
        #         "timeEnd": "12:30:00",
        #         "spaces": 20,
        #         "walkInSpaces": 5,
        #         "displayPublic": True
        #     }
        # }
        # 
        # self.variables_update = {
        #     "input": {
        #         "frequencyType": "WEEKLY",
        #         "frequencyInterval": 2, # Tuesday,
        #         "organizationLocationRoom": to_global_id('OrganizationLocationRoomNode', self.organization_location_room.id),
        #         "organizationClasstype": to_global_id('OrganizationClasstypeNode', self.organization_classtype.id),
        #         "organizationLevel": to_global_id('OrganizationLevelNode', self.organization_level.id),
        #         "dateStart": "1999-01-01",
        #         "dateEnd": "2999-12-31",
        #         "timeStart": "16:00:00",
        #         "timeEnd": "17:30:00",
        #         "spaces": 20,
        #         "walkInSpaces": 5,
        #         "displayPublic": True
        #     }
        # }
        # 
        # self.variables_delete = {
        #     "input": {}
        # }

        self.scheduleshifts_query = '''
  query ScheduleShifts(
      $dateFrom: Date!, 
      $dateUntil:Date!, 
      $orderBy: String, 
      $organizationShift: ID,
      $organizationLocation: ID,
    ){
    scheduleShifts(
        dateFrom:$dateFrom, 
        dateUntil: $dateUntil, 
        orderBy: $orderBy, 
        organizationShift: $organizationShift,
        organizationLocation: $organizationLocation,
    ){
      date
      shifts {
        scheduleItemId
        frequencyType
        date
        status
        description
        holiday
        holidayName
        organizationLocationRoom {
          id
          name
          organizationLocation {
            id
            name
          }
        }
        organizationShift {
          id
          name
        }
        timeStart
        timeEnd
      }
    }
  }
'''

        self.scheduleshift_query = '''
  query ScheduleClass($scheduleItemId: ID!, $date: Date!) {
    scheduleClass(scheduleItemId:$scheduleItemId, date: $date) {
      scheduleItemId
      frequencyType
      organizationLocationRoom {
        id
        name
      }
      organizationClasstype {
        id
        name
      }
      organizationLevel {
        id
        name
      }
      timeStart
      timeEnd
      displayPublic
      bookingStatus
      bookingOpenOn
    }
  }
'''

        self.scheduleshift_create_mutation = ''' 
  mutation CreateScheduleClass($input:CreateScheduleClassInput!) {
    createScheduleClass(input: $input) {
      scheduleItem {
        id
        scheduleItemType
        frequencyType
        frequencyInterval
        organizationLocationRoom {
          id
          name
          organizationLocation {
            id
            name
          }
        }
        organizationClasstype {
          id
          name
        }
        organizationLevel {
          id
          name
        }
        dateStart
        dateEnd
        timeStart
        timeEnd
        displayPublic
      }
    }
  }
'''

        self.scheduleshift_update_mutation = '''
  mutation UpdateScheduleClass($input:UpdateScheduleClassInput!) {
    updateScheduleClass(input: $input) {
      scheduleItem {
        id
        scheduleItemType
        frequencyType
        frequencyInterval
        organizationLocationRoom {
          id
          name
          organizationLocation {
            id
            name
          }
        }
        organizationClasstype {
          id
          name
        }
        organizationLevel {
          id
          name
        }
        dateStart
        dateEnd
        timeStart
        timeEnd
        displayPublic
      }
    }
  }
'''

        self.scheduleshift_delete_mutation = '''
  mutation DeleteScheduleClass($input: DeleteScheduleClassInput!) {
    deleteScheduleClass(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query_input_validation_error_dateUntil_smaller_then_dateFrom(self):
        """ Query list of scheduleshifts
        An error message should be returned if dateUntil < dateFrom
        """
        query = self.scheduleshifts_query

        schedule_shift = f.ScheduleWeeklyShiftFactory.create()
        a_monday = datetime.date(2019, 6, 17)
        variables = {
            'dateFrom': str(a_monday),
            'dateUntil': str(a_monday - datetime.timedelta(days=6)),
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'dateUntil has to be bigger then dateFrom')

    def test_query_input_validation_error_date_input_max_7_days_apart(self):
        """ Query list of scheduleshifts
        An error message should be returned if dates apart > 7 days
        """
        query = self.scheduleshifts_query

        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        a_monday = datetime.date(2019, 6, 17)
        variables = {
            'dateFrom': str(a_monday),
            'dateUntil': str(a_monday + datetime.timedelta(days=31)),
            'attendanceCountType': "ATTENDING_AND_BOOKED"
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], "dateFrom and dateUntil can't be more then 7 days apart")
    
    def test_query(self):
        """ Query list of scheduleshifts """
        query = self.scheduleshifts_query

        schedule_class = f.ScheduleWeeklyShiftFactory.create()

        variables = self.variables_query_list
        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        print("###########")
        print(executed)
        data = executed.get('data')

        self.assertEqual(data['scheduleShifts'][0]['date'], variables['dateFrom'])
        self.assertEqual(
            data['scheduleShifts'][0]['shifts'][0]['scheduleItemId'],
            to_global_id('ScheduleItemNode', schedule_class.id)
        )
        self.assertEqual(
            data['scheduleShifts'][0]['shifts'][0]['organizationShift']['id'],
            to_global_id('OrganizationShiftNode', schedule_class.organization_shift.id)
        )
        self.assertEqual(
            data['scheduleShifts'][0]['shifts'][0]['organizationLocationRoom']['id'],
            to_global_id('OrganizationLocationRoomNode', schedule_class.organization_location_room.id)
        )
        self.assertEqual(
            data['scheduleShifts'][0]['shifts'][0]['timeStart'],
            str(schedule_class.time_start)
        )
        self.assertEqual(
            data['scheduleShifts'][0]['shifts'][0]['timeEnd'],
            str(schedule_class.time_end)
        )
    #
    # def test_query_status_sub(self):
    #     """ Query list sub status of scheduleshift """
    #     query = self.scheduleshifts_query
    #
    #     schedule_class_otc = f.SchedulePublicWeeklyClassOTCFactory.create()
    #     schedule_class = schedule_class_otc.schedule_item
    #
    #     variables = self.variables_query_list_status
    #     executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
    #     data = executed.get('data')
    #
    #     self.assertEqual(data['scheduleShifts'][0]['date'], variables['dateFrom'])
    #     self.assertEqual(
    #         data['scheduleShifts'][0]['shifts'][0]['scheduleItemId'],
    #         to_global_id('ScheduleItemNode', schedule_class.id)
    #     )
    #     self.assertEqual(
    #         data['scheduleShifts'][0]['shifts'][0]['status'],
    #         "SUB"
    #     )
    #
    # def test_query_status_cancelled(self):
    #     """ Query list status cancelled of scheduleshift """
    #     query = self.scheduleshifts_query
    #
    #     schedule_class_otc = f.SchedulePublicWeeklyClassOTCFactory.create()
    #     schedule_class_otc.status = 'CANCELLED'
    #     schedule_class_otc.description = 'Moonday'
    #     schedule_class_otc.save()
    #     schedule_class = schedule_class_otc.schedule_item
    #
    #     variables = self.variables_query_list_status
    #     executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
    #     data = executed.get('data')
    #
    #     self.assertEqual(data['scheduleShifts'][0]['date'], variables['dateFrom'])
    #     self.assertEqual(
    #         data['scheduleShifts'][0]['shifts'][0]['scheduleItemId'],
    #         to_global_id('ScheduleItemNode', schedule_class.id)
    #     )
    #     self.assertEqual(
    #         data['scheduleShifts'][0]['shifts'][0]['status'],
    #         schedule_class_otc.status
    #     )
    #     self.assertEqual(
    #         data['scheduleShifts'][0]['shifts'][0]['description'],
    #         schedule_class_otc.description
    #     )
    #
    # def test_query_status_holiday(self):
    #     """ Query list status holiday of scheduleshift """
    #     query = self.scheduleshifts_query
    #
    #     schedule_class = f.SchedulePublicWeeklyClassFactory.create()
    #     organization_holiday = f.OrganizationHolidayFactory.create()
    #     organization_holiday_location = models.OrganizationHolidayLocation(
    #         organization_holiday = organization_holiday,
    #         organization_location = schedule_class.organization_location_room.organization_location
    #     )
    #     organization_holiday_location.save()
    #
    #     variables = self.variables_query_list_status
    #     executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
    #     data = executed.get('data')
    #
    #     self.assertEqual(data['scheduleShifts'][0]['date'], variables['dateFrom'])
    #     self.assertEqual(
    #         data['scheduleShifts'][0]['shifts'][0]['scheduleItemId'],
    #         to_global_id('ScheduleItemNode', schedule_class.id)
    #     )
    #     self.assertEqual(
    #         data['scheduleShifts'][0]['shifts'][0]['status'],
    #         'CANCELLED'
    #     )
    #     self.assertEqual(
    #         data['scheduleShifts'][0]['shifts'][0]['bookingStatus'],
    #         'HOLIDAY'
    #     )
    #     self.assertEqual(
    #         data['scheduleShifts'][0]['shifts'][0]['holidayName'],
    #         organization_holiday.name
    #     )
    #     self.assertEqual(
    #         data['scheduleShifts'][0]['shifts'][0]['holiday'],
    #         True
    #     )
    #
    # def test_query_status_open(self):
    #     """ Query list status open of scheduleshift """
    #     query = self.scheduleshifts_query
    #
    #     schedule_class_otc = f.SchedulePublicWeeklyClassOTCFactory.create()
    #     schedule_class_otc.status = 'OPEN'
    #     schedule_class_otc.save()
    #     schedule_class = schedule_class_otc.schedule_item
    #
    #     variables = self.variables_query_list_status
    #     executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
    #     data = executed.get('data')
    #
    #     self.assertEqual(data['scheduleShifts'][0]['date'], variables['dateFrom'])
    #     self.assertEqual(
    #         data['scheduleShifts'][0]['shifts'][0]['scheduleItemId'],
    #         to_global_id('ScheduleItemNode', schedule_class.id)
    #     )
    #     self.assertEqual(
    #         data['scheduleShifts'][0]['shifts'][0]['status'],
    #         schedule_class_otc.status
    #     )
    #
    # def test_query_permission_denied_dont_show_nonpublic_shifts(self):
    #     """ Query list of scheduleshifts - check permission denied """
    #     query = self.scheduleshifts_query
    #     schedule_class = f.SchedulePublicWeeklyClassFactory.create()
    #     schedule_class.display_public = False
    #     schedule_class.save()
    #
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     executed = execute_test_client_api_query(query, user, variables=self.variables_query_list)
    #     data = executed['data']
    #     for day in data['scheduleShifts']:
    #         self.assertEqual(len(day['shifts']), 0)
    #
    # def test_query_permission_granted(self):
    #     """ Query list of non public scheduleshifts with view permission """
    #     query = self.scheduleshifts_query
    #     schedule_class = f.SchedulePublicWeeklyClassFactory.create()
    #     schedule_class.display_public = False
    #     schedule_class.save()
    #
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename='view_scheduleshift')
    #     user.user_permissions.add(permission)
    #     user.save()
    #
    #     variables = self.variables_query_list
    #     executed = execute_test_client_api_query(query, user, variables=variables)
    #     data = executed.get('data')
    #
    #     print("##############")
    #     print(executed)
    #
    #     # List all scheduleshifts
    #     self.assertEqual(data['scheduleShifts'][0]['date'], variables['dateFrom'])
    #     self.assertEqual(
    #         data['scheduleShifts'][0]['shifts'][0]['scheduleItemId'],
    #         to_global_id('ScheduleItemNode', schedule_class.id)
    #     )
    #
    # def test_query_filter_organization_classtype(self):
    #     """ Test filtering query by classtype """
    #     query = self.scheduleshifts_query
    #
    #     schedule_class = f.SchedulePublicWeeklyClassFactory.create()
    #     schedule_class2 = f.SchedulePublicWeeklyClassFactory.create()
    #
    #     first_classtype = schedule_class.organization_classtype
    #
    #     second_classtype = schedule_class2.organization_classtype
    #     second_classtype.name = "Second classtype"
    #     second_classtype.save()
    #
    #     variables = self.variables_query_list
    #     variables['organizationClasstype'] = to_global_id('OrganizationClasstypeNode', first_classtype.id)
    #
    #     executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
    #     data = executed.get('data')
    #     for day in data['scheduleShifts']:
    #         for day_class in day['shifts']:
    #             self.assertEqual('Second' not in day_class['organizationClasstype']['name'], True)
    #
    # def test_query_filter_organization_level(self):
    #     """ Test filtering query by level """
    #     query = self.scheduleshifts_query
    #
    #     schedule_class = f.SchedulePublicWeeklyClassFactory.create()
    #     schedule_class2 = f.SchedulePublicWeeklyClassFactory.create()
    #
    #     first_level = schedule_class.organization_level
    #
    #     second_level = schedule_class2.organization_level
    #     second_level.name = "Second level"
    #     second_level.save()
    #
    #     variables = self.variables_query_list
    #     variables['organizationLevel'] = to_global_id('OrganizationLevelNode', first_level.id)
    #
    #     executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
    #     data = executed.get('data')
    #     for day in data['scheduleShifts']:
    #         for day_class in day['shifts']:
    #             self.assertEqual('Second' not in day_class['organizationLevel']['name'], True)
    #
    # def test_query_filter_organization_location(self):
    #     """ Test filtering query by location """
    #     query = self.scheduleshifts_query
    #
    #     schedule_class = f.SchedulePublicWeeklyClassFactory.create()
    #     schedule_class2 = f.SchedulePublicWeeklyClassFactory.create()
    #
    #     first_location_room = schedule_class.organization_location_room
    #     first_location = first_location_room.organization_location
    #
    #     second_location_room = schedule_class2.organization_location_room
    #     second_location_room.name = "Second location room"
    #     second_location_room.save()
    #     second_location = second_location_room.organization_location
    #     second_location.name = "Second location"
    #     second_location.save()
    #
    #     variables = self.variables_query_list
    #     variables['organizationLocation'] = to_global_id('OrganizationLocationNode', first_location.id)
    #
    #     executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
    #     data = executed.get('data')
    #     for day in data['scheduleShifts']:
    #         for day_class in day['shifts']:
    #             self.assertEqual('Second' not in day_class['organizationLocationRoom']['name'], True)
    #
    # def test_query_anon_user(self):
    #     """ Query list of scheduleshifts - anon users can only list public shifts """
    #     query = self.scheduleshifts_query
    #     schedule_class = f.SchedulePublicWeeklyClassFactory.create()
    #     schedule_class.display_public = False
    #     schedule_class.save()
    #
    #     executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query_list)
    #     data = executed['data']
    #     for day in data['scheduleShifts']:
    #         self.assertEqual(len(day['shifts']), 0)
    #
    # def test_query_anon_user_list_public_shifts(self):
    #     """ Query list of scheduleshifts - anon users can only list public shifts """
    #     query = self.scheduleshifts_query
    #     schedule_class = f.SchedulePublicWeeklyClassFactory.create()
    #
    #     executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query_list)
    #     data = executed['data']
    #     self.assertEqual(
    #         data['scheduleShifts'][0]['shifts'][0]['scheduleItemId'],
    #         to_global_id('ScheduleItemNode', schedule_class.id)
    #     )
    #
    # def test_query_one(self):
    #     """ Query one schedule_class as admin """
    #     schedule_class = f.SchedulePublicWeeklyClassFactory.create()
    #     variables = {
    #         "scheduleItemId": to_global_id('ScheduleItemNode', schedule_class.id),
    #         "date": "2014-01-06"
    #     }
    #
    #     # Now query single schedule item and check
    #     executed = execute_test_client_api_query(self.scheduleshift_query, self.admin_user, variables=variables)
    #     data = executed.get('data')
    #
    #     self.assertEqual(data['scheduleClass']['scheduleItemId'], variables['scheduleItemId'])
    #     self.assertEqual(data['scheduleClass']['displayPublic'], schedule_class.display_public)
    #     self.assertEqual(data['scheduleClass']['frequencyType'], schedule_class.frequency_type)
    #     self.assertEqual(data['scheduleClass']['timeStart'], str(schedule_class.time_start))
    #     self.assertEqual(data['scheduleClass']['timeEnd'], str(schedule_class.time_end))
    #     self.assertEqual(data['scheduleClass']['organizationLocationRoom']['id'],
    #                      to_global_id('OrganizationLocationRoomNode', schedule_class.organization_location_room.id))
    #     self.assertEqual(data['scheduleClass']['organizationClasstype']['id'],
    #                      to_global_id('OrganizationClasstypeNode', schedule_class.organization_classtype.id))
    #     self.assertEqual(data['scheduleClass']['organizationLevel']['id'],
    #                      to_global_id('OrganizationLevelNode', schedule_class.organization_level.id))
    #
    # def test_query_one_booking_status_ok(self):
    #     """ Query one schedule_item as admin - booking status ok """
    #     schedule_class = f.SchedulePublicWeeklyClassFactory.create()
    #     schedule_class.spaces = 10
    #     schedule_class.save()
    #
    #     today = datetime.date.today()
    #     next_monday = next_weekday(today, 1)
    #
    #     variables = {
    #         "scheduleItemId": to_global_id('ScheduleItemNode', schedule_class.id),
    #         "date": str(next_monday)
    #     }
    #
    #     # Now query single schedule item and check
    #     executed = execute_test_client_api_query(self.scheduleshift_query, self.admin_user, variables=variables)
    #     data = executed.get('data')
    #
    #     self.assertEqual(data['scheduleClass']['scheduleItemId'], variables['scheduleItemId'])
    #     self.assertEqual(data['scheduleClass']['bookingStatus'], "OK")
    #
    # def test_query_one_booking_status_ongoing(self):
    #     """ Query one schedule_item as admin - booking status ongoing """
    #     now = datetime.datetime.now()
    #     delta = datetime.timedelta(hours=1)
    #
    #     schedule_class = f.SchedulePublicWeeklyClassFactory.create()
    #     schedule_class.frequency_interval = now.date().isoweekday()
    #     schedule_class.time_start = now - delta
    #     schedule_class.time_end = now + delta
    #     schedule_class.spaces = 10
    #     schedule_class.save()
    #
    #     today = datetime.date.today()
    #     next_monday = next_weekday(today, 1)
    #
    #     variables = {
    #         "scheduleItemId": to_global_id('ScheduleItemNode', schedule_class.id),
    #         "date": str(now.date())
    #     }
    #
    #     # Now query single schedule item and check
    #     executed = execute_test_client_api_query(self.scheduleshift_query, self.admin_user, variables=variables)
    #     data = executed.get('data')
    #
    #     self.assertEqual(data['scheduleClass']['scheduleItemId'], variables['scheduleItemId'])
    #     self.assertEqual(data['scheduleClass']['bookingStatus'], "ONGOING")
    #
    # def test_query_one_booking_status_full(self):
    #     """ Query one schedule_item as admin - booking status full """
    #     schedule_class = f.SchedulePublicWeeklyClassFactory.create()
    #     today = datetime.date.today()
    #     next_monday = next_weekday(today, 1)
    #
    #     variables = {
    #         "scheduleItemId": to_global_id('ScheduleItemNode', schedule_class.id),
    #         "date": str(next_monday)
    #     }
    #
    #     # Now query single schedule item and check
    #     executed = execute_test_client_api_query(self.scheduleshift_query, self.admin_user, variables=variables)
    #     data = executed.get('data')
    #
    #     self.assertEqual(data['scheduleClass']['scheduleItemId'], variables['scheduleItemId'])
    #     self.assertEqual(data['scheduleClass']['bookingStatus'], "FULL")
    #
    # def test_query_one_booking_status_cancelled(self):
    #     """ Query one schedule_item as admin - booking status cancelled """
    #     schedule_class = f.SchedulePublicWeeklyClassFactory.create()
    #     schedule_class.status = 'CANCELLED'
    #     schedule_class.save()
    #     today = datetime.date.today()
    #     next_monday = next_weekday(today, 1)
    #
    #     variables = {
    #         "scheduleItemId": to_global_id('ScheduleItemNode', schedule_class.id),
    #         "date": str(next_monday)
    #     }
    #
    #     # Now query single schedule item and check
    #     executed = execute_test_client_api_query(self.scheduleshift_query, self.admin_user, variables=variables)
    #     data = executed.get('data')
    #
    #     self.assertEqual(data['scheduleClass']['scheduleItemId'], variables['scheduleItemId'])
    #     self.assertEqual(data['scheduleClass']['bookingStatus'], "CANCELLED")
    #
    # def test_query_one_booking_status_finished(self):
    #     """ Query one schedule_item as admin - booking status ok """
    #     schedule_class = f.SchedulePublicWeeklyClassFactory.create()
    #     variables = {
    #         "scheduleItemId": to_global_id('ScheduleItemNode', schedule_class.id),
    #         "date": "2014-01-06"
    #     }
    #
    #     # Now query single schedule item and check
    #     executed = execute_test_client_api_query(self.scheduleshift_query, self.admin_user, variables=variables)
    #     data = executed.get('data')
    #
    #     self.assertEqual(data['scheduleClass']['scheduleItemId'], variables['scheduleItemId'])
    #     self.assertEqual(data['scheduleClass']['bookingStatus'], "FINISHED")
    #
    # def test_query_one_booking_status_not_yet_open(self):
    #     """ Query one schedule_item as admin - booking status ok """
    #     schedule_class = f.SchedulePublicWeeklyClassFactory.create()
    #     variables = {
    #         "scheduleItemId": to_global_id('ScheduleItemNode', schedule_class.id),
    #         "date": "2040-01-02"
    #     }
    #
    #     # Now query single schedule item and check
    #     executed = execute_test_client_api_query(self.scheduleshift_query, self.admin_user, variables=variables)
    #     data = executed.get('data')
    #
    #     self.assertEqual(data['scheduleClass']['scheduleItemId'], variables['scheduleItemId'])
    #     self.assertEqual(data['scheduleClass']['bookingStatus'], "NOT_YET_OPEN")
    # #
    # # # def test_query_one_booking_open_on(self):
    # # #     """ Query one schedule_item as admin - booking status ok """
    # # #     schedule_class = f.SchedulePublicWeeklyClassFactory.create()
    # # #     node_id = to_global_id('ScheduleItemNode', schedule_class.id)
    # # #
    # # #     # Now query single schedule item and check
    # # #     executed = execute_test_client_api_query(self.scheduleshift_query, self.admin_user, variables={"id": node_id})
    # # #     data = executed.get('data')
    # # #
    # # #     self.assertEqual(data['scheduleItem']['id'], node_id)
    # # #     self.assertEqual(data['scheduleItem']['frequencyType'], schedule_class.frequency_type)
    # #
    # # def test_query_one_anon_user_non_public(self):
    # #     """ Deny permission for anon users Query one class """
    # #     schedule_class = f.SchedulePublicWeeklyClassFactory.create(display_public=False)
    # #     node_id = to_global_id('ScheduleItemNode', schedule_class.id)
    # #
    # #     # Now query single scheduleshift and check
    # #     executed = execute_test_client_api_query(self.scheduleshift_query, self.anon_user, variables={"id": node_id})
    # #     errors = executed.get('errors')
    # #     self.assertEqual(errors[0]['message'], 'Not logged in!')
    # #
    # # def test_query_one_anon_user_public(self):
    # #     """ Allow anon users to query a public class """
    # #     schedule_class = f.SchedulePublicWeeklyClassFactory.create()
    # #     node_id = to_global_id('ScheduleItemNode', schedule_class.id)
    # #
    # #     # Now query single scheduleshift and check
    # #     executed = execute_test_client_api_query(self.scheduleshift_query, self.anon_user, variables={"id": node_id})
    # #     data = executed.get('data')
    # #     self.assertEqual(data['scheduleItem']['id'], node_id)
    # #
    # # def test_query_one_public(self):
    # #     """ View public shifts as user lacking authorization """
    # #     # Create regular user
    # #     user = f.RegularUserFactory.create()
    # #
    # #     schedule_class = f.SchedulePublicWeeklyClassFactory.create()
    # #     node_id = to_global_id('ScheduleItemNode', schedule_class.id)
    # #
    # #     # Now query single scheduleshift and check
    # #     executed = execute_test_client_api_query(self.scheduleshift_query, user, variables={"id": node_id})
    # #     data = executed.get('data')
    # #     self.assertEqual(data['scheduleItem']['id'], node_id)
    # #
    # # def test_query_one_permission_denied_non_public(self):
    # #     """ Permission denied message when user lacks authorization """
    # #     # Create regular user
    # #     user = f.RegularUserFactory.create()
    # #
    # #     schedule_class = f.SchedulePublicWeeklyClassFactory.create(
    # #         display_public=False
    # #     )
    # #     node_id = to_global_id('ScheduleItemNode', schedule_class.id)
    # #
    # #     # Now query single scheduleshift and check
    # #     executed = execute_test_client_api_query(self.scheduleshift_query, user, variables={"id": node_id})
    # #     errors = executed.get('errors')
    # #     self.assertEqual(errors[0]['message'], 'Permission denied!')
    # #
    # # def test_query_one_permission_granted(self):
    # #     """ Respond with data when user has permission """
    # #     user = f.RegularUserFactory.create()
    # #     permission = Permission.objects.get(codename='view_scheduleshift')
    # #     user.user_permissions.add(permission)
    # #     user.save()
    # #
    # #     schedule_class = f.SchedulePublicWeeklyClassFactory.create()
    # #     node_id = to_global_id('ScheduleItemNode', schedule_class.id)
    # #
    # #     # Now query single location and check
    # #     executed = execute_test_client_api_query(self.scheduleshift_query, user, variables={"id": node_id})
    # #     data = executed.get('data')
    # #     self.assertEqual(data['scheduleItem']['id'], node_id)
    #
    # def test_create_scheduleshift(self):
    #     """ Create a scheduleshift """
    #     query = self.scheduleshift_create_mutation
    #     variables = self.variables_create
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=variables
    #     )
    #     print("@@@@@@@@@@@@@")
    #     print(executed)
    #
    #     data = executed.get('data')
    #     self.assertEqual(data['createScheduleClass']['scheduleItem']['frequencyType'], variables['input']['frequencyType'])
    #     self.assertEqual(data['createScheduleClass']['scheduleItem']['frequencyInterval'], variables['input']['frequencyInterval'])
    #     self.assertEqual(data['createScheduleClass']['scheduleItem']['organizationLocationRoom']['id'], variables['input']['organizationLocationRoom'])
    #     self.assertEqual(data['createScheduleClass']['scheduleItem']['organizationClasstype']['id'], variables['input']['organizationClasstype'])
    #     self.assertEqual(data['createScheduleClass']['scheduleItem']['organizationLevel']['id'], variables['input']['organizationLevel'])
    #     self.assertEqual(data['createScheduleClass']['scheduleItem']['dateStart'], variables['input']['dateStart'])
    #     self.assertEqual(data['createScheduleClass']['scheduleItem']['dateEnd'], variables['input']['dateEnd'])
    #     self.assertEqual(data['createScheduleClass']['scheduleItem']['timeStart'], variables['input']['timeStart'])
    #     self.assertEqual(data['createScheduleClass']['scheduleItem']['timeEnd'], variables['input']['timeEnd'])
    #     self.assertEqual(data['createScheduleClass']['scheduleItem']['displayPublic'], variables['input']['displayPublic'])
    #
    # def test_create_schedule_class_add_all_non_archived_organization_subscription_groups(self):
    #   """
    #   Create a schedule class and check whether a subscription group is added
    #   """
    #   subscription_group = f.OrganizationSubscriptionGroupFactory.create()
    #
    #   query = self.scheduleshift_create_mutation
    #   variables = self.variables_create
    #
    #   executed = execute_test_client_api_query(
    #       query,
    #       self.admin_user,
    #       variables=variables
    #   )
    #
    #   data = executed.get('data')
    #   schedule_item_id = data['createScheduleClass']['scheduleItem']['id']
    #
    #   schedule_item = models.ScheduleItem.objects.get(id=get_rid(schedule_item_id).id)
    #
    #   self.assertEqual(models.ScheduleItemOrganizationSubscriptionGroup.objects.filter(
    #       schedule_item=schedule_item
    #   ).exists(), True)
    #
    # def test_create_schedule_class_add_all_non_archived_organization_classpass_groups(self):
    #   """
    #   Create a schedule class and check whether a classpass group is added
    #   """
    #   classpass_group = f.OrganizationClasspassGroupFactory.create()
    #
    #   query = self.scheduleshift_create_mutation
    #   variables = self.variables_create
    #
    #   executed = execute_test_client_api_query(
    #       query,
    #       self.admin_user,
    #       variables=variables
    #   )
    #
    #   data = executed.get('data')
    #   schedule_item_id = data['createScheduleClass']['scheduleItem']['id']
    #
    #   schedule_item = models.ScheduleItem.objects.get(id=get_rid(schedule_item_id).id)
    #
    #   self.assertEqual(models.ScheduleItemOrganizationClasspassGroup.objects.filter(
    #       schedule_item = schedule_item
    #   ).exists(), True)
    #
    # def test_create_scheduleshift_anon_user(self):
    #     """ Don't allow creating scheduleshifts for non-logged in users """
    #     query = self.scheduleshift_create_mutation
    #     variables = self.variables_create
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.anon_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')
    #
    # def test_create_location_permission_granted(self):
    #     """ Allow creating scheduleshifts for users with permissions """
    #     query = self.scheduleshift_create_mutation
    #     variables = self.variables_create
    #
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename=self.permission_add)
    #     user.user_permissions.add(permission)
    #     user.save()
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['createScheduleClass']['scheduleItem']['frequencyType'],
    #                      variables['input']['frequencyType'])
    #     self.assertEqual(data['createScheduleClass']['scheduleItem']['frequencyInterval'],
    #                      variables['input']['frequencyInterval'])
    #
    # def test_create_scheduleshift_permission_denied(self):
    #     """ Check create scheduleshift permission denied error message """
    #     query = self.scheduleshift_create_mutation
    #     variables = self.variables_create
    #
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')
    #
    # def test_update_scheduleshift(self):
    #     """ Update a scheduleshift """
    #     query = self.scheduleshift_update_mutation
    #     scheduleshift = f.SchedulePublicWeeklyClassFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleshift.pk)
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['updateScheduleClass']['scheduleItem']['id'], variables['input']['id'])
    #     self.assertEqual(data['updateScheduleClass']['scheduleItem']['frequencyType'],
    #                      variables['input']['frequencyType'])
    #     self.assertEqual(data['updateScheduleClass']['scheduleItem']['frequencyInterval'],
    #                      variables['input']['frequencyInterval'])
    #     self.assertEqual(data['updateScheduleClass']['scheduleItem']['organizationLocationRoom']['id'],
    #                      variables['input']['organizationLocationRoom'])
    #     self.assertEqual(data['updateScheduleClass']['scheduleItem']['organizationClasstype']['id'],
    #                      variables['input']['organizationClasstype'])
    #     self.assertEqual(data['updateScheduleClass']['scheduleItem']['organizationLevel']['id'],
    #                      variables['input']['organizationLevel'])
    #     self.assertEqual(data['updateScheduleClass']['scheduleItem']['dateStart'], variables['input']['dateStart'])
    #     self.assertEqual(data['updateScheduleClass']['scheduleItem']['dateEnd'], variables['input']['dateEnd'])
    #     self.assertEqual(data['updateScheduleClass']['scheduleItem']['timeStart'], variables['input']['timeStart'])
    #     self.assertEqual(data['updateScheduleClass']['scheduleItem']['timeEnd'], variables['input']['timeEnd'])
    #     self.assertEqual(data['updateScheduleClass']['scheduleItem']['displayPublic'],
    #                      variables['input']['displayPublic'])
    #
    # def test_update_scheduleshift_anon_user(self):
    #     """ Don't allow updating scheduleshifts for non-logged in users """
    #     query = self.scheduleshift_update_mutation
    #     scheduleshift = f.SchedulePublicWeeklyClassFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleshift.pk)
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.anon_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')
    #
    # def test_update_scheduleshift_permission_granted(self):
    #     """ Allow updating scheduleshifts for users with permissions """
    #     query = self.scheduleshift_update_mutation
    #     scheduleshift = f.SchedulePublicWeeklyClassFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleshift.pk)
    #
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename=self.permission_change)
    #     user.user_permissions.add(permission)
    #     user.save()
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['updateScheduleClass']['scheduleItem']['id'], variables['input']['id'])
    #     self.assertEqual(data['updateScheduleClass']['scheduleItem']['frequencyType'], variables['input']['frequencyType'])
    #
    # def test_update_scheduleshift_permission_denied(self):
    #     """ Check update scheduleshift permission denied error message """
    #     query = self.scheduleshift_update_mutation
    #     scheduleshift = f.SchedulePublicWeeklyClassFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleshift.pk)
    #
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')
    #
    # def test_delete_scheduleshift(self):
    #     """ Delete a scheduleshift """
    #     query = self.scheduleshift_delete_mutation
    #     scheduleshift = f.SchedulePublicWeeklyClassFactory.create()
    #     variables = self.variables_delete
    #     variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleshift.pk)
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['deleteScheduleClass']['ok'], True)
    #
    # def test_delete_scheduleshift_anon_user(self):
    #     """ Delete scheduleshift denied for anon user """
    #     query = self.scheduleshift_delete_mutation
    #     scheduleshift = f.SchedulePublicWeeklyClassFactory.create()
    #     variables = self.variables_delete
    #     variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleshift.pk)
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.anon_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')
    #
    # def test_delete_scheduleshift_permission_granted(self):
    #     """ Allow deleting scheduleshifts for users with permissions """
    #     query = self.scheduleshift_delete_mutation
    #     scheduleshift = f.SchedulePublicWeeklyClassFactory.create()
    #     variables = self.variables_delete
    #     variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleshift.pk)
    #
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename=self.permission_delete)
    #     user.user_permissions.add(permission)
    #     user.save()
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['deleteScheduleClass']['ok'], True)
    #
    # def test_delete_scheduleshift_permission_denied(self):
    #     """ Check delete scheduleshift permission denied error message """
    #     query = self.scheduleshift_delete_mutation
    #     scheduleshift = f.SchedulePublicWeeklyClassFactory.create()
    #     variables = self.variables_delete
    #     variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleshift.pk)
    #
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         user,
    #         variables=variables
    #     )
    #
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')
    #
