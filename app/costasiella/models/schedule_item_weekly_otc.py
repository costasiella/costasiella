from django.utils.translation import gettext as _

from django.db import models


from .organization_classtype import OrganizationClasstype
from .organization_location_room import OrganizationLocationRoom
from .organization_level import OrganizationLevel
from .schedule_item import ScheduleItem

# Create your models here.

class ScheduleItemWeeklyOTC(models.Model):
    class Meta:
        permissions = [
            ('view_scheduleclassweeklyotc', _("Can view schedule class weekly one time change")),
            ('add_scheduleclassweeklyotc', _("Can add schedule class weekly one time change")),
            ('change_scheduleclassweeklyotc', _("Can change schedule class weekly one time change")),
            ('delete_scheduleclassweeklyotc', _("Can delete schedule class weekly one time change")),
        ]

    schedule_item = models.ForeignKey(ScheduleItem, on_delete=models.CASCADE)
    date = models.DateField()
    organization_location_room = models.ForeignKey(OrganizationLocationRoom, on_delete=models.CASCADE, null=True)
    organization_classtype = models.ForeignKey(OrganizationClasstype, on_delete=models.CASCADE, null=True)
    organization_level = models.ForeignKey(OrganizationLevel, on_delete=models.CASCADE, null=True)   
    time_start = models.TimeField(null=True)
    time_end = models.TimeField(null=True)
    # display_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.schedule_item + ' otc [' + str(self.date) + ']'
    
