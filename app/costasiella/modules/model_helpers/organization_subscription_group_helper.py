from django.db.models import Q

from ...models import OrganizationSubscriptionGroup, ScheduleItem, ScheduleItemOrganizationSubscriptionGroup

"""
This helper file is added to allow function to add / remove a group for all schedule items
OrganizationSubscriptionGroup is already imported in the ScheduleItem model. Importing the
Schedule item model in OrganizationSubscription group generates an error.
"""


class OrganizationSubscriptionGroupHelper:
    def add_to_all_classes(self, organization_subscription_group_id):
        """
        Add a new organization subscription group to all classes
        """
        # Get all classes to which this group is added
        schedule_items_already_added = ScheduleItemOrganizationSubscriptionGroup.objects.filter(
            organization_subscription_group=organization_subscription_group_id
        )
        ids = []
        for obj in schedule_items_already_added:
            if obj.schedule_item.id not in ids:
                ids.append(obj.schedule_item.id)

        # Simple filter, don't filter on dates, as users might re-use old classes
        classes_filter = Q(schedule_item_type='CLASS') & ~Q(id__in=ids)
                         
        schedule_items = ScheduleItem.objects.filter(
            classes_filter
        )

        for schedule_item in schedule_items:
            schedule_item_organization_subscription_group = \
                ScheduleItemOrganizationSubscriptionGroup(
                    schedule_item=schedule_item,
                    organization_subscription_group=OrganizationSubscriptionGroup.objects.get(
                        id=organization_subscription_group_id
                    )
                )
            schedule_item_organization_subscription_group.save()

    def remove_from_all_classes(self, organization_subscription_group_id):
        """
        Remove an organization subscription group from all classes when archived
        """
        ScheduleItemOrganizationSubscriptionGroup.objects.filter(
            Q(organization_subscription_group=organization_subscription_group_id)
        ).delete()
