from django.utils.translation import gettext as _
# from graphql.error.located_error import GraphQLLocatedError
import graphql
import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from graphene.test import Client
from graphql_relay import to_global_id

# Create your tests here.
from django.contrib.auth.models import AnonymousUser, Permission

from . import factories as f
from .helpers import execute_test_client_api_query
from .. import models
from .. import schema
from ..modules.gql_tools import get_rid


class GQLScheduleEvent(TestCase):

    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    fixtures = ['app_settings.json']

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_scheduleevent'
        self.permission_add = 'add_scheduleevent'
        self.permission_change = 'change_scheduleevent'
        self.permission_delete = 'delete_scheduleevent'

        # self.account = f.RegularUserFactory.create()
        self.organization_level = f.OrganizationLevelFactory.create()
        self.organization_location = f.OrganizationLocationFactory.create()

        self.variables_query = {
            "archived": False
        }

        self.variables_create = {
            "input": {
                "organizationLocation": to_global_id("OrganizationLocationNode", self.organization_location.id),
                "organizationLevel": to_global_id("OrganizationLevelNode", self.organization_level.id),
                "name": "Created event",
                "tagline": "Tagline for event",
                "preview": "Event preview",
                "description": "Event description",
                "infoMailContent": "hello world"
            }
        }

        self.variables_update = {
            "input": {
                "organizationLocation": to_global_id("OrganizationLocationNode", self.organization_location.id),
                "organizationLevel": to_global_id("OrganizationLevelNode", self.organization_level.id),
                "name": "Updated event",
                "tagline": "Tagline for updated event",
                "preview": "Event preview updated",
                "description": "Event description updated",
                "infoMailContent": "hello world updated"
            }
        }

        self.variables_archive = {
            "input": {
                "archived": True
            }
        }

        self.variables_duplicate = {
            "input": {}
        }

        self.events_query = '''
  query ScheduleEvents($before:String, $after:String, $archived:Boolean!) {
    scheduleEvents(first: 100, before: $before, after:$after, archived:$archived) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          archived
          displayPublic
          displayShop
          autoSendInfoMail
          organizationLocation {
            id
            name
          }
          name
          tagline
          preview
          description
          organizationLevel {
            id
            name
          }
          instructor {
            id 
            fullName
          }
          instructor2 {
            id
            fullName
          }
          dateStart
          dateEnd
          timeStart
          timeEnd
          infoMailContent
          scheduleItems {
            edges {
              node {
                id
              }
            }
          }
          createdAt
          updatedAt
        }
      }
    }
  }
'''

        self.event_query = '''
  query ScheduleEvent($id: ID!) {
    scheduleEvent(id: $id) {
      id
      archived
      displayPublic
      displayShop
      autoSendInfoMail
      organizationLocation {
        id
        name
      }
      name
      tagline
      preview
      description
      organizationLevel {
        id
        name
      }
      instructor {
        id 
        fullName
      }
      instructor2 {
        id
        fullName
      }
      dateStart
      dateEnd
      timeStart
      timeEnd
      infoMailContent
      scheduleItems {
        edges {
          node {
            id
          }
        }
      }
      createdAt
      updatedAt
    }
  }
'''

        self.event_create_mutation = ''' 
  mutation CreateScheduleEvent($input:CreateScheduleEventInput!) {
    createScheduleEvent(input: $input) {
      scheduleEvent{
        id
        displayPublic
        displayShop
        autoSendInfoMail
        organizationLocation {
          id
        }
        organizationLevel {
          id
        }
        name
        tagline
        preview
        description
        infoMailContent
        instructor {
          id
        }
        instructor2 {
          id 
        }
      }
    }
  }
'''

        self.event_update_mutation = '''
  mutation UpdateScheduleEvent($input:UpdateScheduleEventInput!) {
    updateScheduleEvent(input: $input) {
      scheduleEvent{
        id
        displayPublic
        displayShop
        autoSendInfoMail
        organizationLocation {
          id
        }
        organizationLevel {
          id
        }
        name
        tagline
        preview
        description
        infoMailContent
        instructor {
          id
        }
        instructor2 {
          id 
        }
      }
    }
  }
'''

        self.event_archive_mutation = '''
  mutation ArchiveScheduleEvent($input: ArchiveScheduleEventInput!) {
    archiveScheduleEvent(input: $input) {
      scheduleEvent {
        id
        archived
      }
    }
  }
'''

        self.event_duplicate_mutation = '''
  mutation DuplicateScheduleEvent($input: DuplicateScheduleEventInput!) {
    duplicateScheduleEvent(input: $input) {
      scheduleEvent {
        id
        archived
      }
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of schedule events """
        query = self.events_query
        schedule_event = f.ScheduleEventFactory.create()

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query)
        data = executed.get('data')

        self.assertEqual(data['scheduleEvents']['edges'][0]['node']['organizationLocation']['id'],
                         to_global_id("OrganizationLocationNode", schedule_event.organization_location.id))
        self.assertEqual(data['scheduleEvents']['edges'][0]['node']['name'], schedule_event.name)
        self.assertEqual(data['scheduleEvents']['edges'][0]['node']['tagline'], schedule_event.tagline)
        self.assertEqual(data['scheduleEvents']['edges'][0]['node']['preview'], schedule_event.preview)
        self.assertEqual(data['scheduleEvents']['edges'][0]['node']['description'], schedule_event.description)
        self.assertEqual(data['scheduleEvents']['edges'][0]['node']['infoMailContent'],
                         schedule_event.info_mail_content)
        self.assertEqual(data['scheduleEvents']['edges'][0]['node']['organizationLevel']['id'],
                         to_global_id("OrganizationLevelNode", schedule_event.organization_level.id))
        self.assertEqual(data['scheduleEvents']['edges'][0]['node']['instructor']['id'],
                         to_global_id("AccountNode", schedule_event.instructor.id))
        self.assertEqual(data['scheduleEvents']['edges'][0]['node']['instructor2']['id'],
                         to_global_id("AccountNode", schedule_event.instructor_2.id))

    def test_query_permission_denied_dont_show_nonpublic_events(self):
        """ Query list of events - check permission denied
        A user can query the invoices linked to their account, so an error will never be thrown
        But a user shouldn't be able to view orders from other accounts without additional permission
        """
        query = self.events_query
        schedule_event = f.ScheduleEventFactory.create()
        schedule_event.display_public = False
        schedule_event.save()

        # Create regular user
        user = f.RegularUserFactory()
        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        data = executed.get('data')

        # No items should be listed
        self.assertEqual(len(data['scheduleEvents']['edges']), 0)

    def test_query_permission_granted_show_nonpublic_events(self):
        """ Query list of schedule events with view permission """
        query = self.events_query
        schedule_event = f.ScheduleEventFactory.create()
        schedule_event.display_public = False
        schedule_event.save()

        # Create regular user
        user = f.RegularUserFactory()
        permission = Permission.objects.get(codename='view_scheduleevent')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        data = executed.get('data')

        # List all events
        self.assertEqual(data['scheduleEvents']['edges'][0]['node']['organizationLocation']['id'],
                         to_global_id("OrganizationLocationNode", schedule_event.organization_location.id))

    def test_query_anon_user(self):
        """ Query list of schedule events - anon user """
        query = self.events_query
        schedule_event = f.ScheduleEventFactory.create()

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query)
        data = executed.get('data')

        # List all events
        self.assertEqual(data['scheduleEvents']['edges'][0]['node']['organizationLocation']['id'],
                         to_global_id("OrganizationLocationNode", schedule_event.organization_location.id))

    def test_query_one(self):
        """ Query one schedule event as admin """
        schedule_event = f.ScheduleEventFactory.create()

        variables = {
            "id": to_global_id("ScheduleEventNode", schedule_event.id),
        }

        # Now query single invoice and check
        executed = execute_test_client_api_query(self.event_query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['scheduleEvent']['organizationLocation']['id'],
                         to_global_id("OrganizationLocationNode", schedule_event.organization_location.id))
        self.assertEqual(data['scheduleEvent']['name'], schedule_event.name)
        self.assertEqual(data['scheduleEvent']['tagline'], schedule_event.tagline)
        self.assertEqual(data['scheduleEvent']['preview'], schedule_event.preview)
        self.assertEqual(data['scheduleEvent']['description'], schedule_event.description)
        self.assertEqual(data['scheduleEvent']['infoMailContent'],
                         schedule_event.info_mail_content)
        self.assertEqual(data['scheduleEvent']['organizationLevel']['id'],
                         to_global_id("OrganizationLevelNode", schedule_event.organization_level.id))
        self.assertEqual(data['scheduleEvent']['instructor']['id'],
                         to_global_id("AccountNode", schedule_event.instructor.id))
        self.assertEqual(data['scheduleEvent']['instructor2']['id'],
                         to_global_id("AccountNode", schedule_event.instructor_2.id))

    def test_query_one_anon_user_nonpublic_not_allowed(self):
        """ Deny permission for anon users Query one schedule event """
        schedule_event = f.ScheduleEventFactory.create()
        schedule_event.display_public = False
        schedule_event.display_shop = False
        schedule_event.save()

        variables = {
            "id": to_global_id("ScheduleEventNode", schedule_event.id),
        }

        # Now query single invoice and check
        executed = execute_test_client_api_query(self.event_query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_anon_user_public_allowed(self):
        """ Deny permission for anon users Query one schedule event """
        schedule_event = f.ScheduleEventFactory.create()

        variables = {
            "id": to_global_id("ScheduleEventNode", schedule_event.id),
        }

        # Now query single invoice and check
        executed = execute_test_client_api_query(self.event_query, self.anon_user, variables=variables)
        data = executed['data']
        self.assertEqual(data['scheduleEvent']['organizationLocation']['id'],
                         to_global_id("OrganizationLocationNode", schedule_event.organization_location.id))

    def test_query_one_display_nonpublic_permission_denied(self):
        """ Don't list non-public events when user lacks authorization """
        schedule_event = f.ScheduleEventFactory.create()
        schedule_event.display_public = False
        schedule_event.display_shop = False
        schedule_event.save()
        # Create regular user
        user = f.RegularUserFactory()

        variables = {
            "id": to_global_id("ScheduleEventNode", schedule_event.id),
        }

        # Now query single event and check
        executed = execute_test_client_api_query(self.event_query, user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_display_nonpublic_permission_granted(self):
        """ Respond with data when user has permission """
        schedule_event = f.ScheduleEventFactory.create()
        schedule_event.display_public = False
        schedule_event.display_shop = False
        schedule_event.save()
        # Create regular user
        user = f.RegularUserFactory()
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()

        variables = {
            "id": to_global_id("ScheduleEventNode", schedule_event.id),
        }

        # Now query single schedule event and check
        executed = execute_test_client_api_query(self.event_query, user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['scheduleEvent']['organizationLocation']['id'],
                         to_global_id("OrganizationLocationNode", schedule_event.organization_location.id))

    def test_create_schedule_event(self):
        """ Create a schedule event """
        query = self.event_create_mutation
        instructor = f.InstructorFactory.create()
        instructor2 = f.Instructor2Factory.create()
        self.variables_create['input']['instructor'] = to_global_id('AccountNode', instructor.id)
        self.variables_create['input']['instructor2'] = to_global_id('AccountNode', instructor2.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=self.variables_create
        )
        data = executed.get('data')

        self.assertEqual(data['createScheduleEvent']['scheduleEvent']['name'],
                         self.variables_create['input']['name'])
        self.assertEqual(data['createScheduleEvent']['scheduleEvent']['tagline'],
                         self.variables_create['input']['tagline'])
        self.assertEqual(data['createScheduleEvent']['scheduleEvent']['preview'],
                         self.variables_create['input']['preview'])
        self.assertEqual(data['createScheduleEvent']['scheduleEvent']['description'],
                         self.variables_create['input']['description'])
        self.assertEqual(data['createScheduleEvent']['scheduleEvent']['infoMailContent'],
                         self.variables_create['input']['infoMailContent'])
        self.assertEqual(data['createScheduleEvent']['scheduleEvent']['instructor']['id'],
                         self.variables_create['input']['instructor'])
        self.assertEqual(data['createScheduleEvent']['scheduleEvent']['instructor2']['id'],
                         self.variables_create['input']['instructor2'])

    def test_create_schedule_event_full_ticket_added(self):
        """ Create a schedule event and check if the full event ticket is added """
        query = self.event_create_mutation
        instructor = f.InstructorFactory.create()
        instructor2 = f.Instructor2Factory.create()
        self.variables_create['input']['instructor'] = to_global_id('AccountNode', instructor.id)
        self.variables_create['input']['instructor2'] = to_global_id('AccountNode', instructor2.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=self.variables_create
        )
        data = executed.get('data')

        self.assertEqual(data['createScheduleEvent']['scheduleEvent']['name'],
                         self.variables_create['input']['name'])

        gql_id = data['createScheduleEvent']['scheduleEvent']['id']
        rid = get_rid(gql_id)

        schedule_event = models.ScheduleEvent.objects.get(pk=rid.id)
        schedule_event_ticket = models.ScheduleEventTicket.objects.filter(schedule_event=schedule_event).first()

        self.assertEqual(schedule_event_ticket.schedule_event, schedule_event)
        self.assertEqual(schedule_event_ticket.name, "Full event")

    def test_create_event_anon_user(self):
        """ Don't allow creating schedule events for non-logged in users """
        query = self.event_create_mutation
        instructor = f.InstructorFactory.create()
        instructor2 = f.Instructor2Factory.create()
        self.variables_create['input']['instructor'] = to_global_id('AccountNode', instructor.id)
        self.variables_create['input']['instructor2'] = to_global_id('AccountNode', instructor2.id)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=self.variables_create
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_location_permission_granted(self):
        """ Allow creating events for users with permissions """
        query = self.event_create_mutation
        instructor = f.InstructorFactory.create()
        instructor2 = f.Instructor2Factory.create()
        self.variables_create['input']['instructor'] = to_global_id('AccountNode', instructor.id)
        self.variables_create['input']['instructor2'] = to_global_id('AccountNode', instructor2.id)

        account = f.RegularUserFactory.create()
        # Create regular user
        user = account
        permission = Permission.objects.get(codename=self.permission_add)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=self.variables_create
        )
        data = executed.get('data')
        self.assertEqual(data['createScheduleEvent']['scheduleEvent']['name'],
                         self.variables_create['input']['name'])

    def test_create_event_permission_denied(self):
        """ Check create event permission denied error message """
        query = self.event_create_mutation
        instructor = f.InstructorFactory.create()
        instructor2 = f.Instructor2Factory.create()
        self.variables_create['input']['instructor'] = to_global_id('AccountNode', instructor.id)
        self.variables_create['input']['instructor2'] = to_global_id('AccountNode', instructor2.id)

        account = f.RegularUserFactory.create()
        # Create regular user
        user = account
        executed = execute_test_client_api_query(
            query,
            user,
            variables=self.variables_create
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_update_event(self):
        """ Update an event """
        query = self.event_update_mutation
        schedule_event = f.ScheduleEventFactory.create()
        self.variables_update['input']['id'] = to_global_id('ScheduleEventNode', schedule_event.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=self.variables_update
        )
        data = executed.get('data')
        
        self.assertEqual(data['updateScheduleEvent']['scheduleEvent']['name'],
                         self.variables_update['input']['name'])
        self.assertEqual(data['updateScheduleEvent']['scheduleEvent']['tagline'],
                         self.variables_update['input']['tagline'])
        self.assertEqual(data['updateScheduleEvent']['scheduleEvent']['preview'],
                         self.variables_update['input']['preview'])
        self.assertEqual(data['updateScheduleEvent']['scheduleEvent']['description'],
                         self.variables_update['input']['description'])
        self.assertEqual(data['updateScheduleEvent']['scheduleEvent']['infoMailContent'],
                         self.variables_update['input']['infoMailContent'])

    def test_update_event_anon_user(self):
        """ Don't allow updating events for non-logged in users """
        query = self.event_update_mutation
        schedule_event = f.ScheduleEventFactory.create()
        self.variables_update['input']['id'] = to_global_id('ScheduleEventNode', schedule_event.id)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=self.variables_update
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_event_permission_granted(self):
        """ Allow updating event for users with permissions """
        query = self.event_update_mutation
        schedule_event = f.ScheduleEventFactory.create()
        self.variables_update['input']['id'] = to_global_id('ScheduleEventNode', schedule_event.id)

        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_change)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=self.variables_update
        )
        data = executed.get('data')
        self.assertEqual(data['updateScheduleEvent']['scheduleEvent']['name'],
                         self.variables_update['input']['name'])

    def test_update_invoice_permission_denied(self):
        """ Check update event permission denied error message """
        query = self.event_update_mutation
        schedule_event = f.ScheduleEventFactory.create()
        self.variables_update['input']['id'] = to_global_id('ScheduleEventNode', schedule_event.id)

        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=self.variables_update
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_archive_event(self):
        """ Archive an event """
        query = self.event_archive_mutation
        schedule_event = f.ScheduleEventFactory.create()
        self.variables_archive['input']['id'] = to_global_id('ScheduleEventNode', schedule_event.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=self.variables_archive
        )
        data = executed.get('data')
        self.assertEqual(data['archiveScheduleEvent']['scheduleEvent']['id'],
                         to_global_id('ScheduleEventNode', schedule_event.id))
        self.assertEqual(data['archiveScheduleEvent']['scheduleEvent']['archived'],
                         self.variables_archive['input']['archived'])

    def test_archive_event_anon_user(self):
        """ Archive event denied for anon user """
        query = self.event_archive_mutation
        schedule_event = f.ScheduleEventFactory.create()
        self.variables_archive['input']['id'] = to_global_id('ScheduleEventNode', schedule_event.id)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=self.variables_archive
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_archive_event_permission_granted(self):
        """ Allow archive events for users with permissions """
        query = self.event_archive_mutation
        schedule_event = f.ScheduleEventFactory.create()
        self.variables_archive['input']['id'] = to_global_id('ScheduleEventNode', schedule_event.id)

        # Give permissions
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_delete)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=self.variables_archive
        )
        data = executed.get('data')
        self.assertEqual(data['archiveScheduleEvent']['scheduleEvent']['archived'],
                         self.variables_archive['input']['archived'])

    def test_archive_event_permission_denied(self):
        """ Check archive event permission denied error message """
        query = self.event_archive_mutation
        schedule_event = f.ScheduleEventFactory.create()
        self.variables_archive['input']['id'] = to_global_id('ScheduleEventNode', schedule_event.id)

        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=self.variables_archive
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_duplicate_event(self):
        """ Duplicate an event - are all fields duplicated? """
        query = self.event_duplicate_mutation
        schedule_event = f.ScheduleEventFactory.create()
        schedule_event_earlybird = f.ScheduleEventEarlybirdFactory.create(schedule_event=schedule_event)
        schedule_event_ticket = f.ScheduleEventFullTicketFactory.create(schedule_event=schedule_event)
        schedule_item = f.ScheduleItemEventActivityFactory.create(
            schedule_event=schedule_event,
            account=schedule_event.instructor,
            account_2=schedule_event.instructor_2
        )
        schedule_event_media = f.ScheduleEventMediaFactory.create(schedule_event=schedule_event)
        schedule_event.update_dates_and_times()

        self.variables_duplicate['input']['id'] = to_global_id('ScheduleEventNode', schedule_event.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=self.variables_duplicate
        )
        data = executed.get('data')
        # The id of the duplicated event should be returned instead of the given id
        self.assertEqual(
            data['duplicateScheduleEvent']['scheduleEvent']['id'] ==
            to_global_id('ScheduleEventNode', schedule_event.id),
            False
        )
        gql_id = data['duplicateScheduleEvent']['scheduleEvent']['id']
        rid = get_rid(gql_id)

        duplicated_schedule_event = models.ScheduleEvent.objects.get(pk=rid.id)

        # Check schedule event data duplication
        self.assertEqual(schedule_event.archived, duplicated_schedule_event.archived)
        self.assertEqual(duplicated_schedule_event.display_public, False)
        self.assertEqual(duplicated_schedule_event.display_shop, False)
        self.assertEqual(schedule_event.auto_send_info_mail, duplicated_schedule_event.auto_send_info_mail)
        self.assertEqual(schedule_event.name + " (" + _("Duplicated") + ")", duplicated_schedule_event.name)
        self.assertEqual(schedule_event.tagline, duplicated_schedule_event.tagline)
        self.assertEqual(schedule_event.preview, duplicated_schedule_event.preview)
        self.assertEqual(schedule_event.description, duplicated_schedule_event.description)
        self.assertEqual(schedule_event.organization_level, duplicated_schedule_event.organization_level)
        self.assertEqual(schedule_event.instructor, duplicated_schedule_event.instructor)
        self.assertEqual(schedule_event.instructor_2, duplicated_schedule_event.instructor_2)
        self.assertEqual(schedule_event.date_start, duplicated_schedule_event.date_start)
        self.assertEqual(schedule_event.date_end, duplicated_schedule_event.date_end)
        self.assertEqual(schedule_event.time_start, duplicated_schedule_event.time_start)
        self.assertEqual(schedule_event.time_end, duplicated_schedule_event.time_end)
        self.assertEqual(schedule_event.info_mail_content, duplicated_schedule_event.info_mail_content)

        # Check schedule_item duplication
        new_schedule_item = models.ScheduleItem.objects.filter(
            schedule_event=duplicated_schedule_event
        ).first()

        self.assertEqual(schedule_item.schedule_item_type, new_schedule_item.schedule_item_type)
        self.assertEqual(schedule_item.frequency_type, new_schedule_item.frequency_type)
        self.assertEqual(schedule_item.frequency_interval, new_schedule_item.frequency_interval)
        self.assertEqual(schedule_item.organization_location_room, new_schedule_item.organization_location_room)
        self.assertEqual(schedule_item.organization_classtype, new_schedule_item.organization_classtype)
        self.assertEqual(schedule_item.organization_level, new_schedule_item.organization_level)
        self.assertEqual(schedule_item.organization_shift, new_schedule_item.organization_shift)
        self.assertEqual(schedule_item.name, new_schedule_item.name)
        self.assertEqual(schedule_item.spaces, new_schedule_item.spaces)
        self.assertEqual(schedule_item.walk_in_spaces, new_schedule_item.walk_in_spaces)
        self.assertEqual(schedule_item.date_start, new_schedule_item.date_start)
        self.assertEqual(schedule_item.date_end, new_schedule_item.date_end)
        self.assertEqual(schedule_item.time_start, new_schedule_item.time_start)
        self.assertEqual(schedule_item.time_end, new_schedule_item.time_end)
        self.assertEqual(schedule_item.display_public, new_schedule_item.display_public)
        self.assertEqual(schedule_item.info_mail_content, new_schedule_item.info_mail_content)
        self.assertEqual(schedule_item.account, new_schedule_item.account)
        self.assertEqual(schedule_item.account_2, new_schedule_item.account_2)

        # Check ticket data duplication
        new_ticket = models.ScheduleEventTicket.objects.filter(
            schedule_event=duplicated_schedule_event
        ).first()

        self.assertEqual(schedule_event_ticket.full_event, new_ticket.full_event)
        self.assertEqual(schedule_event_ticket.deletable, new_ticket.deletable)
        self.assertEqual(schedule_event_ticket.display_public, new_ticket.display_public)
        self.assertEqual(schedule_event_ticket.name, new_ticket.name)
        self.assertEqual(schedule_event_ticket.description, new_ticket.description)
        self.assertEqual(schedule_event_ticket.price, new_ticket.price)
        self.assertEqual(schedule_event_ticket.finance_tax_rate, new_ticket.finance_tax_rate)
        self.assertEqual(schedule_event_ticket.finance_glaccount, new_ticket.finance_glaccount)
        self.assertEqual(schedule_event_ticket.finance_costcenter, new_ticket.finance_costcenter)

        # Check media data duplication
        new_media = models.ScheduleEventMedia.objects.filter(
            schedule_event=duplicated_schedule_event
        ).first()

        self.assertEqual(schedule_event_media.sort_order, new_media.sort_order)
        self.assertEqual(schedule_event_media.description, new_media.description)
        self.assertEqual(schedule_event_media.image, new_media.image)

        # Check earlybird data duplication
        new_earlybird = models.ScheduleEventEarlybird.objects.filter(
            schedule_event=duplicated_schedule_event
        ).first()

        self.assertEqual(schedule_event_earlybird.date_start, new_earlybird.date_start)
        self.assertEqual(schedule_event_earlybird.date_end, new_earlybird.date_end)
        self.assertEqual(schedule_event_earlybird.discount_percentage, new_earlybird.discount_percentage)

    def test_duplicate_event_anon_user(self):
        """ Duplicate event denied for anon user """
        query = self.event_duplicate_mutation
        schedule_event = f.ScheduleEventFactory.create()
        self.variables_duplicate['input']['id'] = to_global_id('ScheduleEventNode', schedule_event.id)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=self.variables_duplicate
        )

        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_duplicate_event_permission_granted(self):
        """ Allow duplicating events for users with permissions """
        query = self.event_duplicate_mutation
        schedule_event = f.ScheduleEventFactory.create()
        self.variables_duplicate['input']['id'] = to_global_id('ScheduleEventNode', schedule_event.id)

        # Give permissions
        user = schedule_event.instructor
        permission = Permission.objects.get(codename=self.permission_add)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=self.variables_duplicate
        )
        data = executed.get('data')
        # Check if a value returned can be read. If one can be read, all can be read
        self.assertEqual(data['duplicateScheduleEvent']['scheduleEvent']['archived'],
                         schedule_event.archived)

    def test_duplicate_event_permission_denied(self):
        """ Check duplicate event permission denied error message """
        query = self.event_duplicate_mutation
        schedule_event = f.ScheduleEventFactory.create()
        self.variables_duplicate['input']['id'] = to_global_id('ScheduleEventNode', schedule_event.id)

        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=self.variables_duplicate
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')
