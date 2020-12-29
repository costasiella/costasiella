from django.utils.translation import gettext as _

from django.db import models


class ScheduleEventTicketScheduleItem(models.Model):
    schedule_event_ticket = models.ForeignKey('ScheduleEventTicket',
                                              on_delete=models.CASCADE,
                                              related_name="ticket_schedule_items")
    schedule_item = models.ForeignKey('ScheduleItem', on_delete=models.CASCADE)
    included = models.BooleanField(default=False)

    def __str__(self):
        return self.schedule_event_ticket.name + ' [' + self.schedule_item.name + ']'
