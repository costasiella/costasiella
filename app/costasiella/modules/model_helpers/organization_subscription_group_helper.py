from django.db.models import Q

from ...models import OrganizationSubscriptionGroup, ScheduleItem, ScheduleItemOrganizationSubscriptionGroup


class OrganizationSubscriptionGroupHelper:
    def add_to_all_classes(self, organization_subscription_group_id):
        """
        Add a new organization subscription group to all classes
        """
        # Get all classes to which this group is added
        schedule_items_already_added = ScheduleItemOrganizationSubscriptionGroup.objects.filter(
            organization_subscription_group = organization_subscription_group_id
        )
        ids = []
        for obj in schedule_items_already_added:
            if obj.schedule_item.id not in ids:
                ids.append(obj.schedule_item.id)
                
        print(schedule_items_already_added)

        # Simple filter, don't filter on dates, as users might re-use old classes
        classes_filter = Q(schedule_item_type = 'CLASS') & ~Q(id__in=ids)
                         
        schedule_items = ScheduleItem.objects.filter(
            classes_filter
        )

        print(schedule_items)

        for schedule_item in schedule_items:
            schedule_item_organization_subscription_group = \
                ScheduleItemOrganizationSubscriptionGroup(
                    schedule_item = schedule_item,
                    organization_subscription_group = OrganizationSubscriptionGroup(organization_subscription_group_id)
                )
            schedule_item_organization_subscription_group.save()

    
    def remove_from_all_classes(self, organization_subscription_group_id):
        """
        Remove an organization subscription group from all classes when archived
        """
        ScheduleItemOrganizationSubscriptionGroup.objects.filter(
            Q(organization_subscription_group = organization_subscription_group_id)
        ).delete()
    