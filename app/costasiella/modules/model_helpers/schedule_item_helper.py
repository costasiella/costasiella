from django.db.models import Q

from ...models import OrganizationClasspassGroup, OrganizationSubscriptionGroup, ScheduleItem, ScheduleItemOrganizationSubscriptionGroup, ScheduleItemOrganizationClasspassGroup

"""
This helper file is added to allow function to add all subscription groups to a schedule item
ScheduleItem is already imported in the ScheduleItemOrganizationSubscriptionGroup model. 
Importing the SchedulItem model in ScheduleItemOrganizationSubscriptionGroup group generates an error.
"""


class ScheduleItemHelper:
    def add_all_subscription_groups(self, schedule_item_id):
        """
        Add all non-archived subscription groups to this schedule item
        """
        groups = OrganizationSubscriptionGroup.objects.filter(
            archived = False
        )

        for group in groups:
            schedule_item_subscription_group = ScheduleItemOrganizationSubscriptionGroup(
                schedule_item = ScheduleItem.objects.get(id=schedule_item_id),
                organization_subscription_group = group
            ).save()
            
    def add_all_classpass_groups(self, schedule_item_id):
        """
        Add all non-archived classpass groups to this schedule item
        """
        groups = OrganizationClasspassGroup.objects.filter(
            archived = False
        )

        for group in groups:
            schedule_item_classpass_group = ScheduleItemOrganizationClasspassGroup(
                schedule_item = ScheduleItem.objects.get(id=schedule_item_id),
                organization_classpass_group = group
            ).save()
            
