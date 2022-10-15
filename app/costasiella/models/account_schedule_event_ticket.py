from django.db import models

from .account import Account
from .schedule_event_ticket import ScheduleEventTicket


class AccountScheduleEventTicket(models.Model):
    # add additional fields in here
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="schedule_event_tickets")
    schedule_event_ticket = models.ForeignKey(ScheduleEventTicket, on_delete=models.CASCADE, related_name="accounts")
    cancelled = models.BooleanField(default=False)
    payment_confirmation = models.BooleanField(default=False)
    info_mail_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.schedule_event_ticket.schedule_event.name + " " + \
               self.schedule_event_ticket.name + ' ticket for: ' + self.account.full_name

    def set_booking_status_schedule_item_attendances(self, status):
        """
        Cancel all attendance records associated with this ticket
        :return:
        """
        from .schedule_item_attendance import ScheduleItemAttendance

        schedule_item_attendances = ScheduleItemAttendance.objects.filter(
            account_schedule_event_ticket=self
        )

        for schedule_item_attendance in schedule_item_attendances:
            schedule_item_attendance.booking_status = status
            schedule_item_attendance.save()
