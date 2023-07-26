from django.utils.translation import gettext as _

from django.db import models

from .account import Account
from .organization_classtype import OrganizationClasstype
from .organization_location_room import OrganizationLocationRoom
from .organization_level import OrganizationLevel
from .organization_shift import OrganizationShift
from .schedule_item import ScheduleItem

from .choices.instructor_roles import get_instructor_roles
from .choices.schedule_item_otc_statuses import get_schedule_item_otc_statuses

# Create your models here.


class ScheduleItemWeeklyOTC(models.Model):
    INSTRUCTOR_ROLES = get_instructor_roles()
    STATUSES = get_schedule_item_otc_statuses()

    schedule_item = models.ForeignKey(ScheduleItem, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=255, default="", choices=STATUSES)
    description = models.CharField(max_length=255, default="")
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="otc_account")
    role = models.CharField(default="", max_length=50, choices=INSTRUCTOR_ROLES)
    account_2 = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="otc_account_2")
    role_2 = models.CharField(default="", max_length=50, choices=INSTRUCTOR_ROLES)
    organization_location_room = models.ForeignKey(OrganizationLocationRoom, on_delete=models.SET_NULL, null=True)
    organization_classtype = models.ForeignKey(OrganizationClasstype, on_delete=models.SET_NULL, null=True)
    organization_level = models.ForeignKey(OrganizationLevel, on_delete=models.SET_NULL, null=True)   
    organization_shift = models.ForeignKey(OrganizationShift, on_delete=models.SET_NULL, null=True)
    time_start = models.TimeField(null=True)
    time_end = models.TimeField(null=True)
    spaces = models.IntegerField(null=True, default=0,
                                 help_text="Total spaces for this class.")
    walk_in_spaces = models.IntegerField(null=True, default=0,
                                         help_text="Number of walk-in spaces (Can't be booked online).")
    info_mail_enabled = models.BooleanField(default=True)
    info_mail_content = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.schedule_item) + ' otc [' + str(self.date) + ']'

    def on_cancel(self):
        self._cancel_attendances()

    def _cancel_attendances(self):
        from .schedule_item_attendance import ScheduleItemAttendance

        schedule_item_attendances = ScheduleItemAttendance.objects.filter(
            schedule_item=self.schedule_item,
            date=self.date
        )

        for schedule_item_attendance in schedule_item_attendances:
            schedule_item_attendance.cancel()
