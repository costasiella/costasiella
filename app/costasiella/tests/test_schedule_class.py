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
            'dateUntil': str(a_monday + datetime.timedelta(days=6))
        }

        self.variables_create = {
            "input": {
                "name": "New scheduleclass",
                "code" : "123"
            }
        }

        self.variables_update = {
            "input": {
                "name": "Updated scheduleclass",
                "code" : "987"
            }
        }

        self.variables_archive = {
            "input": {
                "archived": True
            }
        }

        self.scheduleclasses_query = '''
  query ScheduleClasses($dateFrom: Date!, $dateUntil:Date!) {
    scheduleClasses(dateFrom:$dateFrom, dateUntil: $dateUntil) {
      date
      classes {
        scheduleItemId
        frequencyType
        date
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
      }
    }
  }
'''

        self.scheduleclass_query = '''
  query ScheduleItem($id: ID!) {
    scheduleItem(id:$id) {
      id
      frequencyType
      frequencyInterval
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
      dateStart
      dateEnd
      timeStart
      timeEnd
      displayPublic
    }
  }
'''

#         self.scheduleclass_create_mutation = ''' 
#   mutation CreateScheduleClass($input:CreateScheduleClassInput!) {
#     createScheduleClass(input: $input) {
#       scheduleClass{
#         id
#         archived
#         name
#         code
#       }
#     }
#   }
# '''

#         self.scheduleclass_update_mutation = '''
#   mutation UpdateScheduleClass($input: UpdateScheduleClassInput!) {
#     updateScheduleClass(input: $input) {
#       scheduleClass {
#         id
#         name
#         code
#       }
#     }
#   }
# '''

#         self.scheduleclass_archive_mutation = '''
#   mutation ArchiveScheduleClass($input: ArchiveScheduleClassInput!) {
#     archiveScheduleClass(input: $input) {
#       scheduleClass {
#         id
#         archived
#       }
#     }
#   }
# '''

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
            'dateUntil': str(a_monday - datetime.timedelta(days=6))
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
            'dateUntil': str(a_monday + datetime.timedelta(days=31))
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], "dateFrom and dateUntil can't be more then 7 days apart")


    def test_query(self):
        """ Query list of scheduleclasses """
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


    def test_query_permision_denied(self):
        """ Query list of scheduleclasses - check permission denied """
        query = self.scheduleclasses_query
        schedule_class = f.SchedulePublicWeeklyClassFactory.create()

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=self.variables_query_list)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_permision_granted(self):
        """ Query list of scheduleclasses with view permission """
        query = self.scheduleclasses_query
        schedule_class = f.SchedulePublicWeeklyClassFactory.create()

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


    def test_query_anon_user(self):
        """ Query list of scheduleclasses - anon user """
        query = self.scheduleclasses_query
        schedule_class = f.SchedulePublicWeeklyClassFactory.create()

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query_list)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one(self):
        """ Query one schedule_item as admin """   
        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        node_id = to_global_id('ScheduleItemNode', schedule_class.id)

        # Now query single schedule item and check
        executed = execute_test_client_api_query(self.scheduleclass_query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')

        self.assertEqual(data['scheduleItem']['id'], node_id)
        self.assertEqual(data['scheduleItem']['frequencyType'], schedule_class.frequency_type)
        self.assertEqual(data['scheduleItem']['frequencyInterval'], schedule_class.frequency_interval)
        self.assertEqual(
          data['scheduleItem']['organizationLocationRoom']['id'], 
          to_global_id('OrganizationLocationRoomNode', schedule_class.organization_location_room.id)
        )
        self.assertEqual(
          data['scheduleItem']['organizationClasstype']['id'], 
          to_global_id('OrganizationClasstypeNode', schedule_class.organization_classtype.id)
        )
        self.assertEqual(
          data['scheduleItem']['organizationLevel']['id'], 
          to_global_id('OrganizationLevelNode', schedule_class.organization_level.id)
        )
        self.assertEqual(data['scheduleItem']['dateStart'], str(schedule_class.date_start))
        self.assertEqual(data['scheduleItem']['dateEnd'], str(schedule_class.date_end))
        self.assertEqual(data['scheduleItem']['timeStart'], str(schedule_class.time_start))
        self.assertEqual(data['scheduleItem']['timeEnd'], str(schedule_class.time_end))
        self.assertEqual(data['scheduleItem']['displayPublic'], schedule_class.display_public)


    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one glacount """   
        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        node_id = to_global_id('ScheduleItemNode', schedule_class.id)

        # Now query single scheduleclass and check
        executed = execute_test_client_api_query(self.scheduleclass_query, self.anon_user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        # Create regular user
        user = f.RegularUserFactory.create()

        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        node_id = to_global_id('ScheduleItemNode', schedule_class.id)

        # Now query single scheduleclass and check
        executed = execute_test_client_api_query(self.scheduleclass_query, user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_scheduleclass')
        user.user_permissions.add(permission)
        user.save()
        
        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        node_id = to_global_id('ScheduleItemNode', schedule_class.id)

        # Now query single location and check   
        executed = execute_test_client_api_query(self.scheduleclass_query, user, variables={"id": node_id})
        print(executed)
        data = executed.get('data')
        self.assertEqual(data['scheduleItem']['id'], node_id)


    # def test_create_scheduleclass(self):
    #     """ Create a scheduleclass """
    #     query = self.scheduleclass_create_mutation
    #     variables = self.variables_create

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['createScheduleClass']['scheduleClass']['name'], variables['input']['name'])
    #     self.assertEqual(data['createScheduleClass']['scheduleClass']['archived'], False)
    #     self.assertEqual(data['createScheduleClass']['scheduleClass']['code'], variables['input']['code'])


    # def test_create_scheduleclass_anon_user(self):
    #     """ Don't allow creating scheduleclasses for non-logged in users """
    #     query = self.scheduleclass_create_mutation
    #     variables = self.variables_create

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_create_location_permission_granted(self):
    #     """ Allow creating scheduleclasses for users with permissions """
    #     query = self.scheduleclass_create_mutation
    #     variables = self.variables_create

    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename=self.permission_add)
    #     user.user_permissions.add(permission)
    #     user.save()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['createScheduleClass']['scheduleClass']['name'], variables['input']['name'])
    #     self.assertEqual(data['createScheduleClass']['scheduleClass']['archived'], False)
    #     self.assertEqual(data['createScheduleClass']['scheduleClass']['code'], variables['input']['code'])


    # def test_create_scheduleclass_permission_denied(self):
    #     """ Check create scheduleclass permission denied error message """
    #     query = self.scheduleclass_create_mutation
    #     variables = self.variables_create

    #     # Create regular user
    #     user = f.RegularUserFactory.create()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')


    # def test_update_scheduleclass(self):
    #     """ Update a scheduleclass """
    #     query = self.scheduleclass_update_mutation
    #     scheduleclass = f.SchedulePublicWeeklyClassFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleclass.pk)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['updateScheduleClass']['scheduleClass']['name'], variables['input']['name'])
    #     self.assertEqual(data['updateScheduleClass']['scheduleClass']['code'], variables['input']['code'])


    # def test_update_scheduleclass_anon_user(self):
    #     """ Don't allow updating scheduleclasses for non-logged in users """
    #     query = self.scheduleclass_update_mutation
    #     scheduleclass = f.SchedulePublicWeeklyClassFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleclass.pk)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_update_scheduleclass_permission_granted(self):
    #     """ Allow updating scheduleclasses for users with permissions """
    #     query = self.scheduleclass_update_mutation
    #     scheduleclass = f.SchedulePublicWeeklyClassFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleclass.pk)

    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename=self.permission_change)
    #     user.user_permissions.add(permission)
    #     user.save()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['updateScheduleClass']['scheduleClass']['name'], variables['input']['name'])
    #     self.assertEqual(data['updateScheduleClass']['scheduleClass']['code'], variables['input']['code'])


    # def test_update_scheduleclass_permission_denied(self):
    #     """ Check update scheduleclass permission denied error message """
    #     query = self.scheduleclass_update_mutation
    #     scheduleclass = f.SchedulePublicWeeklyClassFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleclass.pk)

    #     # Create regular user
    #     user = f.RegularUserFactory.create()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')


    # def test_archive_scheduleclass(self):
    #     """ Archive a scheduleclass """
    #     query = self.scheduleclass_archive_mutation
    #     scheduleclass = f.SchedulePublicWeeklyClassFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleclass.pk)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['archiveScheduleClass']['scheduleClass']['archived'], variables['input']['archived'])


    # def test_unable_to_archive_system_scheduleclass(self):
    #     """ Test that we can't archive a sytem payment method """
    #     query = self.scheduleclass_archive_mutation
    #     # This is the "Cash" system payment method from the fixtures
    #     schedule_class = f.SchedulePublicWeeklyClassFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleclass.pk)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )

    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Unable to archive, this is a system method!')


    # def test_archive_scheduleclass_anon_user(self):
    #     """ Archive scheduleclass denied for anon user """
    #     query = self.scheduleclass_archive_mutation
    #     scheduleclass = f.SchedulePublicWeeklyClassFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleclass.pk)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_archive_scheduleclass_permission_granted(self):
    #     """ Allow archiving scheduleclasses for users with permissions """
    #     query = self.scheduleclass_archive_mutation
    #     scheduleclass = f.SchedulePublicWeeklyClassFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleclass.pk)

    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename=self.permission_delete)
    #     user.user_permissions.add(permission)
    #     user.save()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['archiveScheduleClass']['scheduleClass']['archived'], variables['input']['archived'])


    # def test_archive_scheduleclass_permission_denied(self):
    #     """ Check archive scheduleclass permission denied error message """
    #     query = self.scheduleclass_archive_mutation
    #     scheduleclass = f.SchedulePublicWeeklyClassFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleclass.pk)
        
    #     # Create regular user
    #     user = f.RegularUserFactory.create()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')

