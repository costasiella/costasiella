from django.db.models import Q

from ...models import ScheduleEventTicketScheduleItem, ScheduleItem

"""
This helper file is added to allow functions to add all schedule items to a new ticket
"""


class ScheduleEventTicketScheduleItemHelper:
    def add_schdule_items_to_ticket(self, schedule_event_ticket):
        """
        Add a new schedule item to all tickets
        """
        # Get all tickets to which this group is added
        schedule_items_already_added = ScheduleEventTicketScheduleItem.objects.filter(
            schedule_event_ticket=schedule_event_ticket
        )
        ids = []
        for obj in schedule_items_already_added:
            if obj.schedule_item.id not in ids:
                ids.append(obj.schedule_item.id)

        schedule_items = ScheduleItem.objects.filter(
            Q(schedule_item_type='EVENT_ACTIVITY') &
            Q(schedule_event=schedule_event_ticket.schedule_event) &
            ~Q(id__in=ids)
        )

        for schedule_item in schedule_items:
            schedule_event_ticket_schedule_item = ScheduleEventTicketScheduleItem(
                schedule_item=schedule_item,
                schedule_event_ticket=schedule_event_ticket
            )
            schedule_event_ticket_schedule_item.save()

