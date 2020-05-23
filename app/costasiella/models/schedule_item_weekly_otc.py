from django.utils.translation import gettext as _

from django.db import models

from .account import Account
from .organization_classtype import OrganizationClasstype
from .organization_location_room import OrganizationLocationRoom
from .organization_level import OrganizationLevel
from .schedule_item import ScheduleItem

from .choices.teacher_roles import get_teacher_roles
from .choices.schedule_item_otc_statuses import get_schedule_item_otc_statuses

# Create your models here.


class ScheduleItemWeeklyOTC(models.Model):
    TEACHER_ROLES = get_teacher_roles()
    STATUSES = get_schedule_item_otc_statuses()

    class Meta:
        permissions = [
            ('view_scheduleclassweeklyotc', _("Can view schedule class weekly one time change")),
            ('add_scheduleclassweeklyotc', _("Can add schedule class weekly one time change")),
            ('change_scheduleclassweeklyotc', _("Can change schedule class weekly one time change")),
            ('delete_scheduleclassweeklyotc', _("Can delete schedule class weekly one time change")),
        ]

    schedule_item = models.ForeignKey(ScheduleItem, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=255, default="", choices=STATUSES)
    description = models.CharField(max_length=255, default="")
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="otc_account")
    role = models.CharField(default="", max_length=50, choices=TEACHER_ROLES)
    account_2 = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="otc_account_2")
    role_2 = models.CharField(default="", max_length=50, choices=TEACHER_ROLES)
    organization_location_room = models.ForeignKey(OrganizationLocationRoom, on_delete=models.SET_NULL, null=True)
    organization_classtype = models.ForeignKey(OrganizationClasstype, on_delete=models.SET_NULL, null=True)
    organization_level = models.ForeignKey(OrganizationLevel, on_delete=models.SET_NULL, null=True)   
    time_start = models.TimeField(null=True)
    time_end = models.TimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.schedule_item + ' otc [' + str(self.date) + ']'
    
