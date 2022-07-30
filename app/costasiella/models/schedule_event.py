from django.utils.translation import gettext as _

from django.db import models

from .account import Account
from .organization_location import OrganizationLocation
from .organization_level import OrganizationLevel
from .organization_subscription_group import OrganizationSubscriptionGroup

from .helpers import model_string


class ScheduleEvent(models.Model):
    archived = models.BooleanField(default=False)
    display_public = models.BooleanField(default=False)
    display_shop = models.BooleanField(default=False)
    auto_send_info_mail = models.BooleanField(default=False)
    organization_location = models.ForeignKey(OrganizationLocation, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    tagline = models.CharField(max_length=255, default="")
    preview = models.TextField(default="")
    description = models.TextField(default="")
    organization_level = models.ForeignKey(OrganizationLevel, on_delete=models.CASCADE, null=True)
    instructor = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    instructor_2 = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="instructor_2")
    date_start = models.DateField(null=True)
    date_end = models.DateField(default=None, null=True)
    time_start = models.TimeField(null=True)
    time_end = models.TimeField(null=True)
    info_mail_content = models.TextField(default="")
    organization_subscription_groups = models.ManyToManyField(
        OrganizationSubscriptionGroup,
        through='ScheduleEventSubscriptionGroupDiscount',
        related_name='schedule_event_discounts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return model_string(self)

    def update_dates_and_times(self):
        """
        Set dates & times based on activities.
        After adding/editing/deleting a event schedule item, call this function to update the dates & times
        :return:
        """
        from .schedule_item import ScheduleItem

        schedule_items = ScheduleItem.objects.filter(
            schedule_event=self
        ).order_by("date_start", "time_start")

        time_from = None
        time_until = None
        date_from = None
        date_until = None
        if len(schedule_items) > 0:
            date_from = schedule_items[0].date_start
            date_until = schedule_items[0].date_start
            time_from = schedule_items[0].time_start
            time_until = schedule_items[0].time_end

        if len(schedule_items) > 1:
            date_until = schedule_items[len(schedule_items) - 1].date_start
            time_until = schedule_items[len(schedule_items) - 1].time_end

        self.date_start = date_from
        self.date_end = date_until
        self.time_start = time_from
        self.time_end = time_until

        self.save()

    def get_full_schedule_event_ticket(self):
        """
        Get full event ticket for this event
        :return: models.EventTicket instance
        """
        from .schedule_event_ticket import ScheduleEventTicket

        schedule_event_ticket = ScheduleEventTicket.objects.filter(
            schedule_event=self,
            full_event=True
        ).first()

        return schedule_event_ticket
