from django.utils.translation import gettext as _

from django.db import models
from django.db.models import Q

from .schedule_event import ScheduleEvent
from .schedule_event_ticket_schedule_item import ScheduleEventTicketScheduleItem
from .finance_tax_rate import FinanceTaxRate
from .finance_costcenter import FinanceCostCenter
from .finance_glaccount import FinanceGLAccount


class ScheduleEventTicket(models.Model):
    schedule_event = models.ForeignKey(ScheduleEvent, on_delete=models.CASCADE, related_name="tickets")
    full_event = models.BooleanField(default=False)
    deletable = models.BooleanField(default=True)
    display_public = models.BooleanField(default=True)
    name = models.CharField(max_length=255)
    description = models.TextField(default="")
    price = models.DecimalField(max_digits=20, decimal_places=2)
    schedule_items = models.ManyToManyField(
        'ScheduleItem',
        through='ScheduleEventTicketScheduleItem',
        related_name='schedule_items'
    )
    finance_tax_rate = models.ForeignKey(FinanceTaxRate, on_delete=models.SET_NULL, null=True)
    finance_glaccount = models.ForeignKey(FinanceGLAccount, on_delete=models.SET_NULL, null=True)
    finance_costcenter = models.ForeignKey(FinanceCostCenter, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name + ' [' + str(self.price) + ']'

    def is_sold_out(self):
        """
        Check if this ticket is sold out.
        Sold out when at least 1 activity doesn't have sufficient spaces remaining.
        :return:
        """
        from .schedule_event_ticket_schedule_item import ScheduleEventTicketScheduleItem
        from .schedule_item_attendance import ScheduleItemAttendance

        sold_out = False

        ticket_schedule_items = ScheduleEventTicketScheduleItem.objects.filter(
            schedule_event_ticket=self
        )
        for ticket_schedule_item in ticket_schedule_items:
            schedule_item = ticket_schedule_item.schedule_item
            count_attendance = ScheduleItemAttendance.objects.filter(
                Q(schedule_item=schedule_item) &
                ~Q(booking_status="cancelled")
            ).count()

            if count_attendance >= schedule_item.spaces:
                sold_out = True
                break

        return sold_out
