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


class GQLScheduleShift(TestCase):
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
        
        self.variables_create = {
            "input": {
                "frequencyType": "WEEKLY",
                "frequencyInterval": 1, # Monday,
                "organizationLocationRoom": to_global_id('OrganizationLocationRoomNode', self.organization_location_room.id),
                "organizationShift": to_global_id('OrganizationShiftNode', self.organization_shift.id),
                "dateStart": "2019-01-01",
                "dateEnd": "2999-12-31",
                "timeStart": "11:00:00",
                "timeEnd": "12:30:00",
            }
        }

        self.variables_update = {
            "input": {
                "frequencyType": "WEEKLY",
                "frequencyInterval": 2, # Tuesday,
                "organizationLocationRoom": to_global_id('OrganizationLocationRoomNode', self.organization_location_room.id),
                "organizationShift": to_global_id('OrganizationShiftNode', self.organization_shift.id),
                "dateStart": "1999-01-01",
                "dateEnd": "2999-12-31",
                "timeStart": "16:00:00",
                "timeEnd": "17:30:00"
            }
        }

        self.variables_delete = {
            "input": {}
        }

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
  query ScheduleShift($scheduleItemId: ID!, $date: Date!) {
    scheduleShift(scheduleItemId:$scheduleItemId, date: $date) {
      scheduleItemId
      frequencyType
      organizationLocationRoom {
        id
        name
      }
      organizationShift {
        id
        name
      }
      timeStart
      timeEnd
    }
  }
'''

        self.scheduleshift_create_mutation = ''' 
  mutation CreateScheduleShift($input:CreateScheduleShiftInput!) {
    createScheduleShift(input: $input) {
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
        organizationShift {
          id
          name
        }
        dateStart
        dateEnd
        timeStart
        timeEnd
      }
    }
  }
'''

        self.scheduleshift_update_mutation = '''
  mutation UpdateScheduleShift($input:UpdateScheduleShiftInput!) {
    updateScheduleShift(input: $input) {
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
        organizationShift {
          id
          name
        }
        dateStart
        dateEnd
        timeStart
        timeEnd
      }
    }
  }
'''

        self.scheduleshift_delete_mutation = '''
  mutation DeleteScheduleShift($input: DeleteScheduleShiftInput!) {
    deleteScheduleShift(input: $input) {
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

        schedule_shift = f.ScheduleWeeklyShiftOTCFactory.create()
        a_monday = datetime.date(2019, 6, 17)
        variables = {
            'dateFrom': str(a_monday),
            'dateUntil': str(a_monday + datetime.timedelta(days=31)),
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], "dateFrom and dateUntil can't be more then 7 days apart")
    
    def test_query(self):
        """ Query list of scheduleshifts """
        query = self.scheduleshifts_query

        schedule_shift = f.ScheduleWeeklyShiftFactory.create()

        variables = self.variables_query_list
        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['scheduleShifts'][0]['date'], variables['dateFrom'])
        self.assertEqual(
            data['scheduleShifts'][0]['shifts'][0]['scheduleItemId'],
            to_global_id('ScheduleItemNode', schedule_shift.id)
        )
        self.assertEqual(
            data['scheduleShifts'][0]['shifts'][0]['organizationShift']['id'],
            to_global_id('OrganizationShiftNode', schedule_shift.organization_shift.id)
        )
        self.assertEqual(
            data['scheduleShifts'][0]['shifts'][0]['organizationLocationRoom']['id'],
            to_global_id('OrganizationLocationRoomNode', schedule_shift.organization_location_room.id)
        )
        self.assertEqual(
            data['scheduleShifts'][0]['shifts'][0]['timeStart'],
            str(schedule_shift.time_start)
        )
        self.assertEqual(
            data['scheduleShifts'][0]['shifts'][0]['timeEnd'],
            str(schedule_shift.time_end)
        )

    def test_query_status_cancelled(self):
        """ Query list status cancelled of scheduleshift """
        query = self.scheduleshifts_query

        schedule_shift_otc = f.ScheduleWeeklyShiftOTCFactory.create()
        schedule_shift_otc.status = 'CANCELLED'
        schedule_shift_otc.description = 'No staff required this day'
        schedule_shift_otc.save()
        schedule_shift = schedule_shift_otc.schedule_item

        variables = self.variables_query_list_status
        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['scheduleShifts'][0]['date'], variables['dateFrom'])
        self.assertEqual(
            data['scheduleShifts'][0]['shifts'][0]['scheduleItemId'],
            to_global_id('ScheduleItemNode', schedule_shift.id)
        )
        self.assertEqual(
            data['scheduleShifts'][0]['shifts'][0]['status'],
            schedule_shift_otc.status
        )
        self.assertEqual(
            data['scheduleShifts'][0]['shifts'][0]['description'],
            schedule_shift_otc.description
        )

    def test_query_status_holiday(self):
        """ Query list status holiday of scheduleshift """
        query = self.scheduleshifts_query

        schedule_shift_otc = f.ScheduleWeeklyShiftOTCFactory.create()
        organization_holiday = f.OrganizationHolidayFactory.create()
        organization_holiday_location = models.OrganizationHolidayLocation(
            organization_holiday = organization_holiday,
            organization_location = schedule_shift_otc.organization_location_room.organization_location
        )
        organization_holiday_location.save()

        variables = self.variables_query_list_status
        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['scheduleShifts'][0]['date'], variables['dateFrom'])
        self.assertEqual(
            data['scheduleShifts'][0]['shifts'][0]['scheduleItemId'],
            to_global_id('ScheduleItemNode', schedule_shift_otc.schedule_item.id)
        )
        self.assertEqual(
            data['scheduleShifts'][0]['shifts'][0]['status'],
            'CANCELLED'
        )
        self.assertEqual(
            data['scheduleShifts'][0]['shifts'][0]['holidayName'],
            organization_holiday.name
        )
        self.assertEqual(
            data['scheduleShifts'][0]['shifts'][0]['holiday'],
            True
        )

    def test_query_status_open(self):
        """ Query list status open of scheduleshift """
        query = self.scheduleshifts_query

        schedule_shift_otc = f.ScheduleWeeklyShiftOTCFactory.create()
        schedule_shift_otc.status = 'OPEN'
        schedule_shift_otc.save()
        schedule_shift = schedule_shift_otc.schedule_item

        variables = self.variables_query_list_status
        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['scheduleShifts'][0]['date'], variables['dateFrom'])
        self.assertEqual(
            data['scheduleShifts'][0]['shifts'][0]['scheduleItemId'],
            to_global_id('ScheduleItemNode', schedule_shift.id)
        )
        self.assertEqual(
            data['scheduleShifts'][0]['shifts'][0]['status'],
            schedule_shift_otc.status
        )

    def test_query_permission_denied(self):
        """ Query list of scheduleshifts - check permission denied """
        query = self.scheduleshifts_query
        schedule_shift_otc = f.ScheduleWeeklyShiftOTCFactory.create()

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=self.variables_query_list)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_permission_granted(self):
        """ Query list of scheduleshifts with view permission """
        query = self.scheduleshifts_query
        schedule_shift_otc = f.ScheduleWeeklyShiftOTCFactory.create()
        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()

        variables = self.variables_query_list
        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all scheduleshifts
        self.assertEqual(data['scheduleShifts'][0]['date'], variables['dateFrom'])
        self.assertEqual(
            data['scheduleShifts'][0]['shifts'][0]['scheduleItemId'],
            to_global_id('ScheduleItemNode', schedule_shift_otc.schedule_item.id)
        )

    def test_query_filter_organization_shift(self):
        """ Test filtering query by shift """
        query = self.scheduleshifts_query

        schedule_shift = f.ScheduleWeeklyShiftOTCFactory.create()
        schedule_shift2 = f.ScheduleWeeklyShiftOTCFactory.create(
            account=schedule_shift.account,
            account_2=schedule_shift.account_2
        )

        first_shift = schedule_shift.organization_shift

        second_shift = schedule_shift2.organization_shift
        second_shift.name = "Second shift"
        second_shift.save()

        variables = self.variables_query_list
        variables['organizationShift'] = to_global_id('OrganizationShiftNode', first_shift.id)

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        for day in data['scheduleShifts']:
            for day_class in day['shifts']:
                self.assertEqual('Second' not in day_class['organizationShift']['name'], True)

    def test_query_filter_organization_location(self):
        """ Test filtering query by location """
        query = self.scheduleshifts_query

        schedule_shift = f.ScheduleWeeklyShiftOTCFactory.create()
        schedule_shift2 = f.ScheduleWeeklyShiftOTCFactory.create(
            account=schedule_shift.account,
            account_2=schedule_shift.account_2
        )

        first_location_room = schedule_shift.organization_location_room
        first_location = first_location_room.organization_location

        second_location_room = schedule_shift2.organization_location_room
        second_location_room.name = "Second location room"
        second_location_room.save()
        second_location = second_location_room.organization_location
        second_location.name = "Second location"
        second_location.save()

        variables = self.variables_query_list
        variables['organizationLocation'] = to_global_id('OrganizationLocationNode', first_location.id)

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        for day in data['scheduleShifts']:
            for day_class in day['shifts']:
                self.assertEqual('Second' not in day_class['organizationLocationRoom']['name'], True)

    def test_query_anon_user(self):
        """ Query list of scheduleshifts - anon users can only list public shifts """
        query = self.scheduleshifts_query
        schedule_shift = f.ScheduleWeeklyShiftOTCFactory.create()

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query_list)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query one schedule_shift as admin """
        schedule_shift = f.ScheduleWeeklyShiftFactory.create()
        variables = {
            "scheduleItemId": to_global_id('ScheduleItemNode', schedule_shift.id),
            "date": "2021-12-27"
        }

        # Now query single schedule item and check
        executed = execute_test_client_api_query(self.scheduleshift_query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['scheduleShift']['scheduleItemId'], variables['scheduleItemId'])
        self.assertEqual(data['scheduleShift']['frequencyType'], schedule_shift.frequency_type)
        self.assertEqual(data['scheduleShift']['timeStart'], str(schedule_shift.time_start))
        self.assertEqual(data['scheduleShift']['timeEnd'], str(schedule_shift.time_end))
        self.assertEqual(data['scheduleShift']['organizationLocationRoom']['id'],
                         to_global_id('OrganizationLocationRoomNode', schedule_shift.organization_location_room.id))
        self.assertEqual(data['scheduleShift']['organizationShift']['id'],
                         to_global_id('OrganizationShiftNode', schedule_shift.organization_shift.id))


    def test_query_one_anon_user(self):
        """ Anon users aren't allowed to query a shift """
        schedule_shift = f.ScheduleWeeklyShiftFactory.create()
        node_id = to_global_id('ScheduleItemNode', schedule_shift.id)

        # Now query single scheduleshift and check
        executed = execute_test_client_api_query(self.scheduleshift_query, self.anon_user, variables={
            "scheduleItemId": node_id,
            "date": "2021-12-27"
        })
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """
        # Create regular user
        user = f.RegularUserFactory.create()

        schedule_shift = f.ScheduleWeeklyShiftFactory.create()
        node_id = to_global_id('ScheduleItemNode', schedule_shift.id)

        # Now query single scheduleshift and check
        executed = execute_test_client_api_query(self.scheduleshift_query, user, variables={
            "scheduleItemId": node_id,
            "date": "2021-12-27"
        })
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_scheduleshift')
        user.user_permissions.add(permission)
        user.save()

        schedule_shift = f.ScheduleWeeklyShiftFactory.create()
        variables = {
            "scheduleItemId": to_global_id('ScheduleItemNode', schedule_shift.id),
            "date": "2021-12-27"
        }

        # Now query single location and check
        executed = execute_test_client_api_query(self.scheduleshift_query, user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['scheduleShift']['scheduleItemId'], variables['scheduleItemId'])

    def test_create_scheduleshift(self):
        """ Create a scheduleshift """
        query = self.scheduleshift_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(data['createScheduleShift']['scheduleItem']['frequencyType'],
                         variables['input']['frequencyType'])
        self.assertEqual(data['createScheduleShift']['scheduleItem']['frequencyInterval'],
                         variables['input']['frequencyInterval'])
        self.assertEqual(data['createScheduleShift']['scheduleItem']['organizationLocationRoom']['id'],
                         variables['input']['organizationLocationRoom'])
        self.assertEqual(data['createScheduleShift']['scheduleItem']['organizationShift']['id'],
                         variables['input']['organizationShift'])
        self.assertEqual(data['createScheduleShift']['scheduleItem']['dateStart'], variables['input']['dateStart'])
        self.assertEqual(data['createScheduleShift']['scheduleItem']['dateEnd'], variables['input']['dateEnd'])
        self.assertEqual(data['createScheduleShift']['scheduleItem']['timeStart'], variables['input']['timeStart'])
        self.assertEqual(data['createScheduleShift']['scheduleItem']['timeEnd'], variables['input']['timeEnd'])

    def test_create_scheduleshift_anon_user(self):
        """ Don't allow creating scheduleshifts for non-logged in users """
        query = self.scheduleshift_create_mutation
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
        """ Allow creating scheduleshifts for users with permissions """
        query = self.scheduleshift_create_mutation
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
        self.assertEqual(data['createScheduleShift']['scheduleItem']['frequencyType'],
                         variables['input']['frequencyType'])
        self.assertEqual(data['createScheduleShift']['scheduleItem']['frequencyInterval'],
                         variables['input']['frequencyInterval'])

    def test_create_scheduleshift_permission_denied(self):
        """ Check create scheduleshift permission denied error message """
        query = self.scheduleshift_create_mutation
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

    def test_update_scheduleshift(self):
        """ Update a scheduleshift """
        query = self.scheduleshift_update_mutation
        scheduleshift = f.ScheduleWeeklyShiftFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleshift.pk)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(data['updateScheduleShift']['scheduleItem']['id'], variables['input']['id'])
        self.assertEqual(data['updateScheduleShift']['scheduleItem']['frequencyType'],
                         variables['input']['frequencyType'])
        self.assertEqual(data['updateScheduleShift']['scheduleItem']['frequencyInterval'],
                         variables['input']['frequencyInterval'])
        self.assertEqual(data['updateScheduleShift']['scheduleItem']['organizationLocationRoom']['id'],
                         variables['input']['organizationLocationRoom'])
        self.assertEqual(data['updateScheduleShift']['scheduleItem']['organizationShift']['id'],
                         variables['input']['organizationShift'])
        self.assertEqual(data['updateScheduleShift']['scheduleItem']['dateStart'], variables['input']['dateStart'])
        self.assertEqual(data['updateScheduleShift']['scheduleItem']['dateEnd'], variables['input']['dateEnd'])
        self.assertEqual(data['updateScheduleShift']['scheduleItem']['timeStart'], variables['input']['timeStart'])
        self.assertEqual(data['updateScheduleShift']['scheduleItem']['timeEnd'], variables['input']['timeEnd'])

    def test_update_scheduleshift_anon_user(self):
        """ Don't allow updating scheduleshifts for non-logged in users """
        query = self.scheduleshift_update_mutation
        scheduleshift = f.ScheduleWeeklyShiftFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleshift.pk)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_scheduleshift_permission_granted(self):
        """ Allow updating scheduleshifts for users with permissions """
        query = self.scheduleshift_update_mutation
        scheduleshift = f.ScheduleWeeklyShiftFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleshift.pk)

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
        self.assertEqual(data['updateScheduleShift']['scheduleItem']['id'], variables['input']['id'])
        self.assertEqual(data['updateScheduleShift']['scheduleItem']['frequencyType'],
                         variables['input']['frequencyType'])

    def test_update_scheduleshift_permission_denied(self):
        """ Check update scheduleshift permission denied error message """
        query = self.scheduleshift_update_mutation
        scheduleshift = f.ScheduleWeeklyShiftFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleshift.pk)

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

    def test_delete_scheduleshift(self):
        """ Delete a scheduleshift """
        query = self.scheduleshift_delete_mutation
        scheduleshift = f.ScheduleWeeklyShiftFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleshift.pk)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteScheduleShift']['ok'], True)

    def test_delete_scheduleshift_anon_user(self):
        """ Delete scheduleshift denied for anon user """
        query = self.scheduleshift_delete_mutation
        scheduleshift = f.ScheduleWeeklyShiftFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleshift.pk)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_scheduleshift_permission_granted(self):
        """ Allow deleting scheduleshifts for users with permissions """
        query = self.scheduleshift_delete_mutation
        scheduleshift = f.ScheduleWeeklyShiftFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleshift.pk)

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
        self.assertEqual(data['deleteScheduleShift']['ok'], True)

    def test_delete_scheduleshift_permission_denied(self):
        """ Check delete scheduleshift permission denied error message """
        query = self.scheduleshift_delete_mutation
        scheduleshift = f.ScheduleWeeklyShiftFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleshift.pk)

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

