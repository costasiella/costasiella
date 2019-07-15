from django.utils import timezone
from django.db.models import Q


from ...models import OrganizationSubscriptionGroup, ScheduleItem


class OrganizationSubscriptionGroupHelper:
    def add_to_all_classes(self, organization_group_id):
        """
        Add a new organization subscription group to all classes
        """
        now = timezone.now()

        classes_filter = Q(schedule_item_type = 'CLASS') & \
            (
                # Classes on this day (Specific)
                (
                    Q(frequency_type = 'SPECIFIC') & \
                    Q(date_start__gte = now.date())
                ) | # OR
                # Weekly classes
                ( 
                    Q(frequency_type = 'WEEKLY') &
                    Q(date_start__lte = now.date()) & 
                    (Q(date_end__gte = now.date()) | Q(date_end__isnull = True ))
                )
            )
    
        schedule_items = ScheduleItem.objects.filter(
            classes_filter
        )

        print(schedule_items)