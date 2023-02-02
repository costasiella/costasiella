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

        self.permission_view = 'view_scheduleclass'
        self.permission_add = 'add_scheduleclass'
        self.permission_change = 'change_scheduleclass'
        self.permission_delete = 'delete_scheduleclass'

        a_monday = datetime.date(2019, 6, 17)
        self.variables_query_list = {
            'dateFrom': str(a_monday),
            'dateUntil': str(a_monday + datetime.timedelta(days=6)),
        }

        a_last_friday_of_the_month = datetime.date(2022, 4, 29)
        self.variables_query_last_weekday_of_month_list = {
            'dateFrom': str(a_last_friday_of_the_month),
            'dateUntil': str(a_last_friday_of_the_month + datetime.timedelta(days=6)),
        }

        status_monday = datetime.date(2030, 12, 30)
        self.variables_query_list_status = {
            'dateFrom': str(status_monday),
            'dateUntil': str(status_monday + datetime.timedelta(days=6)),
        }

        self.organization_location_room = f.OrganizationLocationRoomFactory.create()
        self.organization_classtype = f.OrganizationClasstypeFactory.create()
        self.organization_level = f.OrganizationLevelFactory.create()

        self.variables_create = {
            "input": {
                "frequencyType": "WEEKLY",
                "frequencyInterval": 1,  # Monday,
                "organizationLocationRoom": to_global_id('OrganizationLocationRoomNode', self.organization_location_room.id),
                "organizationClasstype": to_global_id('OrganizationClasstypeNode', self.organization_classtype.id),
                "organizationLevel": to_global_id('OrganizationLevelNode', self.organization_level.id),
                "dateStart": "2019-01-01",
                "dateEnd": "2999-12-31",
                "timeStart": "11:00:00",
                "timeEnd": "12:30:00",
                "spaces": 20,
                "walkInSpaces": 5,
                "enrollmentSpaces": 10,
                "displayPublic": True,
                "infoMailEnabled": False
            }
        }

        self.variables_create_last_weekday_of_month = {
            "input": {
                "frequencyType": "LAST_WEEKDAY_OF_MONTH",
                "frequencyInterval": 1,  # Monday,
                "organizationLocationRoom": to_global_id('OrganizationLocationRoomNode', self.organization_location_room.id),
                "organizationClasstype": to_global_id('OrganizationClasstypeNode', self.organization_classtype.id),
                "organizationLevel": to_global_id('OrganizationLevelNode', self.organization_level.id),
                "dateStart": "2019-01-01",
                "dateEnd": "2999-12-31",
                "timeStart": "11:00:00",
                "timeEnd": "12:30:00",
                "spaces": 20,
                "walkInSpaces": 5,
                "displayPublic": True
            }
        }

        self.variables_update = {
            "input": {
                "frequencyType": "WEEKLY",
                "frequencyInterval": 2,  # Tuesday,
                "organizationLocationRoom": to_global_id('OrganizationLocationRoomNode', self.organization_location_room.id),
                "organizationClasstype": to_global_id('OrganizationClasstypeNode', self.organization_classtype.id),
                "organizationLevel": to_global_id('OrganizationLevelNode', self.organization_level.id),
                "dateStart": "1999-01-01",
                "dateEnd": "2999-12-31",
                "timeStart": "16:00:00",
                "timeEnd": "17:30:00",
                "spaces": 20,
                "walkInSpaces": 5,
                "enrollmentSpaces": 12,
                "displayPublic": True,
                "infoMailEnabled": False
            }
        }

        self.variables_update_last_weekday_of_month = {
            "input": {
                "frequencyType": "LAST_WEEKDAY_OF_MONTH",
                "frequencyInterval": 2,  # Tuesday,
                "organizationLocationRoom": to_global_id('OrganizationLocationRoomNode', self.organization_location_room.id),
                "organizationClasstype": to_global_id('OrganizationClasstypeNode', self.organization_classtype.id),
                "organizationLevel": to_global_id('OrganizationLevelNode', self.organization_level.id),
                "dateStart": "1999-01-01",
                "dateEnd": "2999-12-31",
                "timeStart": "16:00:00",
                "timeEnd": "17:30:00",
                "spaces": 20,
                "walkInSpaces": 5,
                "displayPublic": True
            }
        }

        self.variables_delete = {
            "input": {}
        }

        self.scheduleclasses_query = '''
  query ScheduleClasses(
      $dateFrom: Date!, 
      $dateUntil:Date!, 
      $orderBy: String, 
      $instructor: ID,
      $organizationClasstype: ID,
      $organizationLevel: ID,
      $organizationLocation: ID,
    ){
    scheduleClasses(
        dateFrom:$dateFrom, 
        dateUntil: $dateUntil, 
        orderBy: $orderBy, 
        instructor: $instructor,
        organizationClasstype: $organizationClasstype,
        organizationLevel: $organizationLevel,
        organizationLocation: $organizationLocation,
        publicOnly: false
    ){
      date
      classes {
        scheduleItemId
        frequencyType
        date
        status
        description
        holiday
        holidayName
        account {
          id
        }
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
        timeStart
        timeEnd
        displayPublic
        bookingStatus
        enrollmentSpaces
      }
    }
  }
'''

        self.scheduleclass_query = '''
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
      infoMailEnabled
      enrollmentSpaces
    }
  }
'''

        self.scheduleclass_create_mutation = ''' 
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
        infoMailEnabled
        enrollmentSpaces
      }
    }
  }
'''

        self.scheduleclass_update_mutation = '''
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
        infoMailEnabled
        enrollmentSpaces
      }
    }
  }
'''

        self.scheduleclass_delete_mutation = '''
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
        """ Query list of scheduleclasses
        An error message should be returned if dateUntil < dateFrom
        """
        query = self.scheduleclasses_query

        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        a_monday = datetime.date(2019, 6, 17)
        variables = {
            'dateFrom': str(a_monday),
            'dateUntil': str(a_monday - datetime.timedelta(days=6)),
            'attendanceCountType': "ATTENDING_AND_BOOKED"
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'dateUntil has to be bigger then dateFrom')

    def test_query_input_validation_error_date_input_max_7_days_apart(self):
        """ Query list of scheduleclasses
        An error message should be returned if dates apart > 7 days
        """
        query = self.scheduleclasses_query

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

    def test_query_weekly(self):
        """ Query list of weekly scheduleclasses """
        query = self.scheduleclasses_query

        schedule_class = f.SchedulePublicWeeklyClassFactory.create()

        variables = self.variables_query_list
        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['scheduleClasses'][0]['date'], variables['dateFrom'])
        self.assertEqual(
            data['scheduleClasses'][0]['classes'][0]['scheduleItemId'],
            to_global_id('ScheduleItemNode', schedule_class.id)
        )
        self.assertEqual(
            data['scheduleClasses'][0]['classes'][0]['organizationClasstype']['id'],
            to_global_id('OrganizationClasstypeNode', schedule_class.organization_classtype.id)
        )
        self.assertEqual(
            data['scheduleClasses'][0]['classes'][0]['organizationLocationRoom']['id'],
            to_global_id('OrganizationLocationRoomNode', schedule_class.organization_location_room.id)
        )
        self.assertEqual(
            data['scheduleClasses'][0]['classes'][0]['organizationLevel']['id'],
            to_global_id('OrganizationLevelNode', schedule_class.organization_level.id)
        )
        self.assertEqual(
            data['scheduleClasses'][0]['classes'][0]['timeStart'],
            str(schedule_class.time_start)
        )
        self.assertEqual(
            data['scheduleClasses'][0]['classes'][0]['timeEnd'],
            str(schedule_class.time_end)
        )
        self.assertEqual(
            data['scheduleClasses'][0]['classes'][0]['displayPublic'],
            schedule_class.display_public
        )
        self.assertEqual(
            data['scheduleClasses'][0]['classes'][0]['enrollmentSpaces'],
            schedule_class.enrollment_spaces
        )

    def test_query_last_weekday_of_month(self):
        """ Query list of monthly classes within the last week """
        query = self.scheduleclasses_query

        schedule_class = f.SchedulePublicLastWeekdayOfMonthClassFactory.create()

        variables = self.variables_query_last_weekday_of_month_list
        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['scheduleClasses'][0]['date'], variables['dateFrom'])
        self.assertEqual(
            data['scheduleClasses'][0]['classes'][0]['scheduleItemId'],
            to_global_id('ScheduleItemNode', schedule_class.id)
        )
        self.assertEqual(
            data['scheduleClasses'][0]['classes'][0]['organizationClasstype']['id'],
            to_global_id('OrganizationClasstypeNode', schedule_class.organization_classtype.id)
        )
        self.assertEqual(
            data['scheduleClasses'][0]['classes'][0]['organizationLocationRoom']['id'],
            to_global_id('OrganizationLocationRoomNode', schedule_class.organization_location_room.id)
        )
        self.assertEqual(
            data['scheduleClasses'][0]['classes'][0]['organizationLevel']['id'],
            to_global_id('OrganizationLevelNode', schedule_class.organization_level.id)
        )
        self.assertEqual(
            data['scheduleClasses'][0]['classes'][0]['timeStart'],
            str(schedule_class.time_start)
        )
        self.assertEqual(
            data['scheduleClasses'][0]['classes'][0]['timeEnd'],
            str(schedule_class.time_end)
        )
        self.assertEqual(
            data['scheduleClasses'][0]['classes'][0]['displayPublic'],
            schedule_class.display_public
        )

    def test_query_status_sub(self):
        """ Query list sub status of scheduleclass """
        query = self.scheduleclasses_query

        schedule_class_otc = f.SchedulePublicWeeklyClassOTCFactory.create()
        schedule_class = schedule_class_otc.schedule_item

        variables = self.variables_query_list_status
        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['scheduleClasses'][0]['date'], variables['dateFrom'])
        self.assertEqual(
            data['scheduleClasses'][0]['classes'][0]['scheduleItemId'],
            to_global_id('ScheduleItemNode', schedule_class.id)
        )
        self.assertEqual(
            data['scheduleClasses'][0]['classes'][0]['status'],
            "SUB"
        )

    def test_query_status_cancelled(self):
        """ Query list status cancelled of scheduleclass """
        query = self.scheduleclasses_query

        schedule_class_otc = f.SchedulePublicWeeklyClassOTCFactory.create()
        schedule_class_otc.status = 'CANCELLED'
        schedule_class_otc.description = 'Moonday'
        schedule_class_otc.save()
        schedule_class = schedule_class_otc.schedule_item

        variables = self.variables_query_list_status
        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['scheduleClasses'][0]['date'], variables['dateFrom'])
        self.assertEqual(
            data['scheduleClasses'][0]['classes'][0]['scheduleItemId'],
            to_global_id('ScheduleItemNode', schedule_class.id)
        )
        self.assertEqual(
            data['scheduleClasses'][0]['classes'][0]['status'],
            schedule_class_otc.status
        )
        self.assertEqual(
            data['scheduleClasses'][0]['classes'][0]['description'],
            schedule_class_otc.description
        )

    def test_query_status_holiday(self):
        """ Query list status holiday of scheduleclass """
        query = self.scheduleclasses_query

        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        organization_holiday = f.OrganizationHolidayFactory.create()
        organization_holiday_location = models.OrganizationHolidayLocation(
            organization_holiday = organization_holiday,
            organization_location = schedule_class.organization_location_room.organization_location
        )
        organization_holiday_location.save()

        variables = self.variables_query_list_status
        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['scheduleClasses'][0]['date'], variables['dateFrom'])
        self.assertEqual(
            data['scheduleClasses'][0]['classes'][0]['scheduleItemId'],
            to_global_id('ScheduleItemNode', schedule_class.id)
        )
        self.assertEqual(
            data['scheduleClasses'][0]['classes'][0]['status'],
            'CANCELLED'
        )
        self.assertEqual(
            data['scheduleClasses'][0]['classes'][0]['bookingStatus'],
            'HOLIDAY'
        )
        self.assertEqual(
            data['scheduleClasses'][0]['classes'][0]['holidayName'],
            organization_holiday.name
        )
        self.assertEqual(
            data['scheduleClasses'][0]['classes'][0]['holiday'],
            True
        )

    def test_query_status_open(self):
        """ Query list status open of scheduleclass """
        query = self.scheduleclasses_query

        schedule_class_otc = f.SchedulePublicWeeklyClassOTCFactory.create()
        schedule_class_otc.status = 'OPEN'
        schedule_class_otc.save()
        schedule_class = schedule_class_otc.schedule_item

        variables = self.variables_query_list_status
        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['scheduleClasses'][0]['date'], variables['dateFrom'])
        self.assertEqual(
            data['scheduleClasses'][0]['classes'][0]['scheduleItemId'],
            to_global_id('ScheduleItemNode', schedule_class.id)
        )
        self.assertEqual(
            data['scheduleClasses'][0]['classes'][0]['status'],
            schedule_class_otc.status
        )

    def test_query_permission_denied_dont_show_nonpublic_classes(self):
        """ Query list of scheduleclasses - check permission denied """
        query = self.scheduleclasses_query
        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        schedule_class.display_public = False
        schedule_class.save()

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=self.variables_query_list)
        data = executed['data']
        for day in data['scheduleClasses']:
            self.assertEqual(len(day['classes']), 0)

    def test_query_permission_granted(self):
        """ Query list of non public scheduleclasses with view permission """
        query = self.scheduleclasses_query
        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        schedule_class.display_public = False
        schedule_class.save()

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_scheduleclass')
        user.user_permissions.add(permission)
        user.save()

        variables = self.variables_query_list
        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all scheduleclasses
        self.assertEqual(data['scheduleClasses'][0]['date'], variables['dateFrom'])
        self.assertEqual(
            data['scheduleClasses'][0]['classes'][0]['scheduleItemId'],
            to_global_id('ScheduleItemNode', schedule_class.id)
        )

    def test_query_filter_instructor(self):
        """ Test filtering query by instructor """
        query = self.scheduleclasses_query

        schedule_item_account = f.ScheduleItemAccountFactory(
            account=f.InstructorFactory.create(),
            account_2=None
        )

        # By switching this around, the second class shouldn't appear in the search results
        schedule_item_account_2 = f.ScheduleItemAccountFactory(
            account=f.Instructor2Factory.create(),
            account_2=None
        )

        variables = self.variables_query_list
        variables['instructor'] = to_global_id('AccountNode', schedule_item_account.account.id)

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        for day in data['scheduleClasses']:
            for day_class in day['classes']:
                self.assertEqual(day_class['account']['id'], variables['instructor'])

    def test_query_filter_organization_classtype(self):
        """ Test filtering query by classtype """
        query = self.scheduleclasses_query

        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        schedule_class2 = f.SchedulePublicWeeklyClassFactory.create()

        first_classtype = schedule_class.organization_classtype

        second_classtype = schedule_class2.organization_classtype
        second_classtype.name = "Second classtype"
        second_classtype.save()

        variables = self.variables_query_list
        variables['organizationClasstype'] = to_global_id('OrganizationClasstypeNode', first_classtype.id)

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        for day in data['scheduleClasses']:
            for day_class in day['classes']:
                self.assertEqual('Second' not in day_class['organizationClasstype']['name'], True)

    def test_query_filter_organization_level(self):
        """ Test filtering query by level """
        query = self.scheduleclasses_query

        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        schedule_class2 = f.SchedulePublicWeeklyClassFactory.create()

        first_level = schedule_class.organization_level

        second_level = schedule_class2.organization_level
        second_level.name = "Second level"
        second_level.save()

        variables = self.variables_query_list
        variables['organizationLevel'] = to_global_id('OrganizationLevelNode', first_level.id)

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        for day in data['scheduleClasses']:
            for day_class in day['classes']:
                self.assertEqual('Second' not in day_class['organizationLevel']['name'], True)

    def test_query_filter_organization_location(self):
        """ Test filtering query by location """
        query = self.scheduleclasses_query

        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        schedule_class2 = f.SchedulePublicWeeklyClassFactory.create()

        first_location_room = schedule_class.organization_location_room
        first_location = first_location_room.organization_location

        second_location_room = schedule_class2.organization_location_room
        second_location_room.name = "Second location room"
        second_location_room.save()
        second_location = second_location_room.organization_location
        second_location.name = "Second location"
        second_location.save()

        variables = self.variables_query_list
        variables['organizationLocation'] = to_global_id('OrganizationLocationNode', first_location.id)

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        for day in data['scheduleClasses']:
            for day_class in day['classes']:
                self.assertEqual('Second' not in day_class['organizationLocationRoom']['name'], True)

    def test_query_anon_user(self):
        """ Query list of scheduleclasses - anon users can only list public classes """
        query = self.scheduleclasses_query
        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        schedule_class.display_public = False
        schedule_class.save()

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query_list)
        data = executed['data']
        for day in data['scheduleClasses']:
            self.assertEqual(len(day['classes']), 0)

    def test_query_anon_user_list_public_classes(self):
        """ Query list of scheduleclasses - anon users can only list public classes """
        query = self.scheduleclasses_query
        schedule_class = f.SchedulePublicWeeklyClassFactory.create()

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query_list)
        data = executed['data']
        self.assertEqual(
            data['scheduleClasses'][0]['classes'][0]['scheduleItemId'],
            to_global_id('ScheduleItemNode', schedule_class.id)
        )

    def test_query_one(self):
        """ Query one schedule_class as admin """
        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        variables = {
            "scheduleItemId": to_global_id('ScheduleItemNode', schedule_class.id),
            "date": "2014-01-06"
        }

        # Now query single schedule item and check
        executed = execute_test_client_api_query(self.scheduleclass_query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['scheduleClass']['scheduleItemId'], variables['scheduleItemId'])
        self.assertEqual(data['scheduleClass']['displayPublic'], schedule_class.display_public)
        self.assertEqual(data['scheduleClass']['infoMailEnabled'], schedule_class.info_mail_enabled)
        self.assertEqual(data['scheduleClass']['frequencyType'], schedule_class.frequency_type)
        self.assertEqual(data['scheduleClass']['timeStart'], str(schedule_class.time_start))
        self.assertEqual(data['scheduleClass']['timeEnd'], str(schedule_class.time_end))
        self.assertEqual(data['scheduleClass']['enrollmentSpaces'], schedule_class.enrollment_spaces)
        self.assertEqual(data['scheduleClass']['organizationLocationRoom']['id'],
                         to_global_id('OrganizationLocationRoomNode', schedule_class.organization_location_room.id))
        self.assertEqual(data['scheduleClass']['organizationClasstype']['id'],
                         to_global_id('OrganizationClasstypeNode', schedule_class.organization_classtype.id))
        self.assertEqual(data['scheduleClass']['organizationLevel']['id'],
                         to_global_id('OrganizationLevelNode', schedule_class.organization_level.id))

    def test_query_one_booking_status_ok(self):
        """ Query one schedule_item as admin - booking status ok """
        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        schedule_class.spaces = 10
        schedule_class.save()

        today = datetime.date.today()
        next_monday = next_weekday(today, 1)

        variables = {
            "scheduleItemId": to_global_id('ScheduleItemNode', schedule_class.id),
            "date": str(next_monday)
        }

        # Now query single schedule item and check
        executed = execute_test_client_api_query(self.scheduleclass_query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['scheduleClass']['scheduleItemId'], variables['scheduleItemId'])
        self.assertEqual(data['scheduleClass']['bookingStatus'], "OK")

    def test_query_one_booking_status_ongoing(self):
        """ Query one schedule_item as admin - booking status ongoing """
        now = datetime.datetime.now()
        delta = datetime.timedelta(hours=1)

        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        schedule_class.frequency_interval = now.date().isoweekday()
        schedule_class.time_start = now - delta
        schedule_class.time_end = now + delta
        schedule_class.spaces = 10
        schedule_class.save()

        today = datetime.date.today()
        next_monday = next_weekday(today, 1)

        variables = {
            "scheduleItemId": to_global_id('ScheduleItemNode', schedule_class.id),
            "date": str(now.date())
        }

        # Now query single schedule item and check
        executed = execute_test_client_api_query(self.scheduleclass_query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['scheduleClass']['scheduleItemId'], variables['scheduleItemId'])
        self.assertEqual(data['scheduleClass']['bookingStatus'], "ONGOING")

    def test_query_one_booking_status_full(self):
        """ Query one schedule_item as admin - booking status full """
        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        schedule_class.spaces = 0
        schedule_class.save()

        today = datetime.date.today()
        next_monday = next_weekday(today, 1)

        variables = {
            "scheduleItemId": to_global_id('ScheduleItemNode', schedule_class.id),
            "date": str(next_monday)
        }

        # Now query single schedule item and check
        executed = execute_test_client_api_query(self.scheduleclass_query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['scheduleClass']['scheduleItemId'], variables['scheduleItemId'])
        self.assertEqual(data['scheduleClass']['bookingStatus'], "FULL")

    def test_query_one_booking_status_cancelled(self):
        """ Query one schedule_item as admin - booking status cancelled """
        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        schedule_class.status = 'CANCELLED'
        schedule_class.save()
        today = datetime.date.today()
        next_monday = next_weekday(today, 1)

        variables = {
            "scheduleItemId": to_global_id('ScheduleItemNode', schedule_class.id),
            "date": str(next_monday)
        }

        # Now query single schedule item and check
        executed = execute_test_client_api_query(self.scheduleclass_query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['scheduleClass']['scheduleItemId'], variables['scheduleItemId'])
        self.assertEqual(data['scheduleClass']['bookingStatus'], "CANCELLED")

    def test_query_one_booking_status_finished(self):
        """ Query one schedule_item as admin - booking status ok """
        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        variables = {
            "scheduleItemId": to_global_id('ScheduleItemNode', schedule_class.id),
            "date": "2014-01-06"
        }

        # Now query single schedule item and check
        executed = execute_test_client_api_query(self.scheduleclass_query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['scheduleClass']['scheduleItemId'], variables['scheduleItemId'])
        self.assertEqual(data['scheduleClass']['bookingStatus'], "FINISHED")

    def test_query_one_booking_status_not_yet_open(self):
        """ Query one schedule_item as admin - booking status ok """
        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        variables = {
            "scheduleItemId": to_global_id('ScheduleItemNode', schedule_class.id),
            "date": "2040-01-02"
        }

        # Now query single schedule item and check
        executed = execute_test_client_api_query(self.scheduleclass_query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['scheduleClass']['scheduleItemId'], variables['scheduleItemId'])
        self.assertEqual(data['scheduleClass']['bookingStatus'], "NOT_YET_OPEN")
    #
    # # def test_query_one_booking_open_on(self):
    # #     """ Query one schedule_item as admin - booking status ok """
    # #     schedule_class = f.SchedulePublicWeeklyClassFactory.create()
    # #     node_id = to_global_id('ScheduleItemNode', schedule_class.id)
    # #
    # #     # Now query single schedule item and check
    # #     executed = execute_test_client_api_query(self.scheduleclass_query, self.admin_user, variables={"id": node_id})
    # #     data = executed.get('data')
    # #
    # #     self.assertEqual(data['scheduleItem']['id'], node_id)
    # #     self.assertEqual(data['scheduleItem']['frequencyType'], schedule_class.frequency_type)
    #
    # def test_query_one_anon_user_non_public(self):
    #     """ Deny permission for anon users Query one class """
    #     schedule_class = f.SchedulePublicWeeklyClassFactory.create(display_public=False)
    #     node_id = to_global_id('ScheduleItemNode', schedule_class.id)
    #
    #     # Now query single scheduleclass and check
    #     executed = execute_test_client_api_query(self.scheduleclass_query, self.anon_user, variables={"id": node_id})
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')
    #
    # def test_query_one_anon_user_public(self):
    #     """ Allow anon users to query a public class """
    #     schedule_class = f.SchedulePublicWeeklyClassFactory.create()
    #     node_id = to_global_id('ScheduleItemNode', schedule_class.id)
    #
    #     # Now query single scheduleclass and check
    #     executed = execute_test_client_api_query(self.scheduleclass_query, self.anon_user, variables={"id": node_id})
    #     data = executed.get('data')
    #     self.assertEqual(data['scheduleItem']['id'], node_id)
    #
    # def test_query_one_public(self):
    #     """ View public classes as user lacking authorization """
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #
    #     schedule_class = f.SchedulePublicWeeklyClassFactory.create()
    #     node_id = to_global_id('ScheduleItemNode', schedule_class.id)
    #
    #     # Now query single scheduleclass and check
    #     executed = execute_test_client_api_query(self.scheduleclass_query, user, variables={"id": node_id})
    #     data = executed.get('data')
    #     self.assertEqual(data['scheduleItem']['id'], node_id)
    #
    # def test_query_one_permission_denied_non_public(self):
    #     """ Permission denied message when user lacks authorization """
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #
    #     schedule_class = f.SchedulePublicWeeklyClassFactory.create(
    #         display_public=False
    #     )
    #     node_id = to_global_id('ScheduleItemNode', schedule_class.id)
    #
    #     # Now query single scheduleclass and check
    #     executed = execute_test_client_api_query(self.scheduleclass_query, user, variables={"id": node_id})
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')
    #
    # def test_query_one_permission_granted(self):
    #     """ Respond with data when user has permission """
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename='view_scheduleclass')
    #     user.user_permissions.add(permission)
    #     user.save()
    #
    #     schedule_class = f.SchedulePublicWeeklyClassFactory.create()
    #     node_id = to_global_id('ScheduleItemNode', schedule_class.id)
    #
    #     # Now query single location and check
    #     executed = execute_test_client_api_query(self.scheduleclass_query, user, variables={"id": node_id})
    #     data = executed.get('data')
    #     self.assertEqual(data['scheduleItem']['id'], node_id)

    def test_create_scheduleclass_weekly_min_7_days_delta_start_and_end_date(self):
        """ Check that at least 7 days should be between start & end for weekly classes """
        query = self.scheduleclass_create_mutation
        variables = self.variables_create
        variables['input']['dateStart'] = "2022-01-01"
        variables['input']['dateEnd'] = "2022-01-04"

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )

        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'There should be at least 7 days between start and end dates!')

    def test_create_scheduleclass_last_weekday_of_month_min_7_days_delta_start_and_end_date(self):
        """ Check that at least 31 days should be between start & end for last weekday of month classes """
        query = self.scheduleclass_create_mutation
        variables = self.variables_create_last_weekday_of_month
        variables['input']['dateStart'] = "2022-01-01"
        variables['input']['dateEnd'] = "2022-01-04"

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )

        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'There should be at least 31 days between start and end dates!')

    def test_create_scheduleclass_weekly(self):
        """ Create a weekly scheduleclass """
        query = self.scheduleclass_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(data['createScheduleClass']['scheduleItem']['frequencyType'],
                         variables['input']['frequencyType'])
        self.assertEqual(data['createScheduleClass']['scheduleItem']['frequencyInterval'],
                         variables['input']['frequencyInterval'])
        self.assertEqual(data['createScheduleClass']['scheduleItem']['organizationLocationRoom']['id'],
                         variables['input']['organizationLocationRoom'])
        self.assertEqual(data['createScheduleClass']['scheduleItem']['organizationClasstype']['id'],
                         variables['input']['organizationClasstype'])
        self.assertEqual(data['createScheduleClass']['scheduleItem']['organizationLevel']['id'],
                         variables['input']['organizationLevel'])
        self.assertEqual(data['createScheduleClass']['scheduleItem']['dateStart'],
                         variables['input']['dateStart'])
        self.assertEqual(data['createScheduleClass']['scheduleItem']['dateEnd'],
                         variables['input']['dateEnd'])
        self.assertEqual(data['createScheduleClass']['scheduleItem']['timeStart'],
                         variables['input']['timeStart'])
        self.assertEqual(data['createScheduleClass']['scheduleItem']['timeEnd'],
                         variables['input']['timeEnd'])
        self.assertEqual(data['createScheduleClass']['scheduleItem']['displayPublic'],
                         variables['input']['displayPublic'])
        self.assertEqual(data['createScheduleClass']['scheduleItem']['infoMailEnabled'],
                         variables['input']['infoMailEnabled'])
        self.assertEqual(data['createScheduleClass']['scheduleItem']['enrollmentSpaces'],
                         variables['input']['enrollmentSpaces'])

    def test_create_scheduleclass_last_weekday_of_month(self):
        """ Create a weekly scheduleclass """
        query = self.scheduleclass_create_mutation
        variables = self.variables_create_last_weekday_of_month

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(data['createScheduleClass']['scheduleItem']['frequencyType'],
                         variables['input']['frequencyType'])
        self.assertEqual(data['createScheduleClass']['scheduleItem']['frequencyInterval'],
                         variables['input']['frequencyInterval'])
        self.assertEqual(data['createScheduleClass']['scheduleItem']['organizationLocationRoom']['id'],
                         variables['input']['organizationLocationRoom'])
        self.assertEqual(data['createScheduleClass']['scheduleItem']['organizationClasstype']['id'],
                         variables['input']['organizationClasstype'])
        self.assertEqual(data['createScheduleClass']['scheduleItem']['organizationLevel']['id'],
                         variables['input']['organizationLevel'])
        self.assertEqual(data['createScheduleClass']['scheduleItem']['dateStart'],
                         variables['input']['dateStart'])
        self.assertEqual(data['createScheduleClass']['scheduleItem']['dateEnd'],
                         variables['input']['dateEnd'])
        self.assertEqual(data['createScheduleClass']['scheduleItem']['timeStart'],
                         variables['input']['timeStart'])
        self.assertEqual(data['createScheduleClass']['scheduleItem']['timeEnd'],
                         variables['input']['timeEnd'])
        self.assertEqual(data['createScheduleClass']['scheduleItem']['displayPublic'],
                         variables['input']['displayPublic'])

    def test_create_schedule_class_add_all_non_archived_organization_subscription_groups(self):
      """
      Create a schedule class and check whether a subscription group is added
      """
      subscription_group = f.OrganizationSubscriptionGroupFactory.create()

      query = self.scheduleclass_create_mutation
      variables = self.variables_create

      executed = execute_test_client_api_query(
          query,
          self.admin_user,
          variables=variables
      )

      data = executed.get('data')
      schedule_item_id = data['createScheduleClass']['scheduleItem']['id']

      schedule_item = models.ScheduleItem.objects.get(id=get_rid(schedule_item_id).id)

      self.assertEqual(models.ScheduleItemOrganizationSubscriptionGroup.objects.filter(
          schedule_item=schedule_item
      ).exists(), True)

    def test_create_schedule_class_add_all_non_archived_organization_classpass_groups(self):
      """
      Create a schedule class and check whether a classpass group is added
      """
      classpass_group = f.OrganizationClasspassGroupFactory.create()

      query = self.scheduleclass_create_mutation
      variables = self.variables_create

      executed = execute_test_client_api_query(
          query,
          self.admin_user,
          variables=variables
      )

      data = executed.get('data')
      schedule_item_id = data['createScheduleClass']['scheduleItem']['id']

      schedule_item = models.ScheduleItem.objects.get(id=get_rid(schedule_item_id).id)

      self.assertEqual(models.ScheduleItemOrganizationClasspassGroup.objects.filter(
          schedule_item = schedule_item
      ).exists(), True)

    def test_create_scheduleclass_anon_user(self):
        """ Don't allow creating scheduleclasses for non-logged in users """
        query = self.scheduleclass_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_location_permission_granted(self):
        """ Allow creating scheduleclasses for users with permissions """
        query = self.scheduleclass_create_mutation
        variables = self.variables_create

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_add)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createScheduleClass']['scheduleItem']['frequencyType'],
                         variables['input']['frequencyType'])
        self.assertEqual(data['createScheduleClass']['scheduleItem']['frequencyInterval'],
                         variables['input']['frequencyInterval'])

    def test_create_scheduleclass_permission_denied(self):
        """ Check create scheduleclass permission denied error message """
        query = self.scheduleclass_create_mutation
        variables = self.variables_create

        # Create regular user
        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_update_scheduleclass_weekly(self):
        """ Update a weekly scheduleclass """
        query = self.scheduleclass_update_mutation
        scheduleclass = f.SchedulePublicWeeklyClassFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleclass.pk)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateScheduleClass']['scheduleItem']['id'], variables['input']['id'])
        self.assertEqual(data['updateScheduleClass']['scheduleItem']['frequencyType'],
                         variables['input']['frequencyType'])
        self.assertEqual(data['updateScheduleClass']['scheduleItem']['frequencyInterval'],
                         variables['input']['frequencyInterval'])
        self.assertEqual(data['updateScheduleClass']['scheduleItem']['organizationLocationRoom']['id'],
                         variables['input']['organizationLocationRoom'])
        self.assertEqual(data['updateScheduleClass']['scheduleItem']['organizationClasstype']['id'],
                         variables['input']['organizationClasstype'])
        self.assertEqual(data['updateScheduleClass']['scheduleItem']['organizationLevel']['id'],
                         variables['input']['organizationLevel'])
        self.assertEqual(data['updateScheduleClass']['scheduleItem']['dateStart'], variables['input']['dateStart'])
        self.assertEqual(data['updateScheduleClass']['scheduleItem']['dateEnd'], variables['input']['dateEnd'])
        self.assertEqual(data['updateScheduleClass']['scheduleItem']['timeStart'], variables['input']['timeStart'])
        self.assertEqual(data['updateScheduleClass']['scheduleItem']['timeEnd'], variables['input']['timeEnd'])
        self.assertEqual(data['updateScheduleClass']['scheduleItem']['displayPublic'],
                         variables['input']['displayPublic'])
        self.assertEqual(data['updateScheduleClass']['scheduleItem']['infoMailEnabled'],
                         variables['input']['infoMailEnabled'])
        self.assertEqual(data['updateScheduleClass']['scheduleItem']['enrollmentSpaces'],
                         variables['input']['enrollmentSpaces'])

    def test_update_scheduleclass_last_weekday_of_month(self):
        """ Update a scheduleclass """
        query = self.scheduleclass_update_mutation
        scheduleclass = f.SchedulePublicWeeklyClassFactory.create()
        variables = self.variables_update_last_weekday_of_month
        variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleclass.pk)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateScheduleClass']['scheduleItem']['id'], variables['input']['id'])
        self.assertEqual(data['updateScheduleClass']['scheduleItem']['frequencyType'],
                         variables['input']['frequencyType'])
        self.assertEqual(data['updateScheduleClass']['scheduleItem']['frequencyInterval'],
                         variables['input']['frequencyInterval'])
        self.assertEqual(data['updateScheduleClass']['scheduleItem']['organizationLocationRoom']['id'],
                         variables['input']['organizationLocationRoom'])
        self.assertEqual(data['updateScheduleClass']['scheduleItem']['organizationClasstype']['id'],
                         variables['input']['organizationClasstype'])
        self.assertEqual(data['updateScheduleClass']['scheduleItem']['organizationLevel']['id'],
                         variables['input']['organizationLevel'])
        self.assertEqual(data['updateScheduleClass']['scheduleItem']['dateStart'], variables['input']['dateStart'])
        self.assertEqual(data['updateScheduleClass']['scheduleItem']['dateEnd'], variables['input']['dateEnd'])
        self.assertEqual(data['updateScheduleClass']['scheduleItem']['timeStart'], variables['input']['timeStart'])
        self.assertEqual(data['updateScheduleClass']['scheduleItem']['timeEnd'], variables['input']['timeEnd'])
        self.assertEqual(data['updateScheduleClass']['scheduleItem']['displayPublic'],
                         variables['input']['displayPublic'])

    def test_update_scheduleclass_anon_user(self):
        """ Don't allow updating scheduleclasses for non-logged in users """
        query = self.scheduleclass_update_mutation
        scheduleclass = f.SchedulePublicWeeklyClassFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleclass.pk)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_scheduleclass_permission_granted(self):
        """ Allow updating scheduleclasses for users with permissions """
        query = self.scheduleclass_update_mutation
        scheduleclass = f.SchedulePublicWeeklyClassFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleclass.pk)

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_change)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateScheduleClass']['scheduleItem']['id'], variables['input']['id'])
        self.assertEqual(data['updateScheduleClass']['scheduleItem']['frequencyType'], variables['input']['frequencyType'])

    def test_update_scheduleclass_permission_denied(self):
        """ Check update scheduleclass permission denied error message """
        query = self.scheduleclass_update_mutation
        scheduleclass = f.SchedulePublicWeeklyClassFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleclass.pk)

        # Create regular user
        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )

        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_delete_scheduleclass(self):
        """ Delete a scheduleclass """
        query = self.scheduleclass_delete_mutation
        scheduleclass = f.SchedulePublicWeeklyClassFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleclass.pk)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteScheduleClass']['ok'], True)

    def test_delete_scheduleclass_anon_user(self):
        """ Delete scheduleclass denied for anon user """
        query = self.scheduleclass_delete_mutation
        scheduleclass = f.SchedulePublicWeeklyClassFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleclass.pk)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_scheduleclass_permission_granted(self):
        """ Allow deleting scheduleclasses for users with permissions """
        query = self.scheduleclass_delete_mutation
        scheduleclass = f.SchedulePublicWeeklyClassFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleclass.pk)

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_delete)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteScheduleClass']['ok'], True)

    def test_delete_scheduleclass_permission_denied(self):
        """ Check delete scheduleclass permission denied error message """
        query = self.scheduleclass_delete_mutation
        scheduleclass = f.SchedulePublicWeeklyClassFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleclass.pk)

        # Create regular user
        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )

        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

