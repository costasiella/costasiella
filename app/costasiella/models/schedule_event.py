from django.utils.translation import gettext as _

from django.db import models

from .account import Account
from .organization_location import OrganizationLocation
from .organization_level import OrganizationLevel


class ScheduleEvent(models.Model):
    SCHEDULE_ITEM_TYPES = (
        ('CLASS', _("Class")),
        ('APPOINTMENT', _("Appointment"))
    )

    archived = models.BooleanField(default=False)
    display_public = models.BooleanField(default=True)
    auto_send_info_mail = models.BooleanField(default=False)
    organization_location = models.ForeignKey(OrganizationLocation, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    tagline = models.CharField(max_length=255)
    preview = models.TextField(default="")
    description = models.TextField(default="")
    organization_level = models.ForeignKey(OrganizationLevel, on_delete=models.CASCADE, null=True)
    teacher = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    teacher_2 = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="teacher_2")
    date_start = models.DateField(null=True)
    date_end = models.DateField(default=None, null=True)
    time_start = models.TimeField(null=True)
    time_end = models.TimeField(null=True)
    info_mail_content = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name + ' [' + str(self.date_start) + ']'
