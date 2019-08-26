from django.utils.translation import gettext as _

from django.db import models


from .organization_classtype import OrganizationClasstype
from .organization_location_room import OrganizationLocationRoom
from .organization_level import OrganizationLevel
from .organization_classpass_group import OrganizationClasspassGroup
from .organization_subscription_group import OrganizationSubscriptionGroup

# Create your models here.

class ScheduleItem(models.Model):
    class Meta:
        permissions = [
            ('view_scheduleclass', _("Can view schedule class")),
            ('add_scheduleclass', _("Can add schedule class")),
            ('change_scheduleclass', _("Can change schedule class")),
            ('delete_scheduleclass', _("Can delete schedule class")),
            ('view_scheduleappointment', _("Can view schedule appointment")),
            ('add_scheduleappointment', _("Can add schedule appointment")),
            ('change_scheduleappointment', _("Can change schedule appointment")),
            ('delete_scheduleappointment', _("Can delete schedule appointment")),
        ]

    SCHEDULE_ITEM_TYPES = (
        ('CLASS', _("Class")),
        ('APPOINTMENT', _("Appointment"))
    )

    FREQUENCY_TYPES = (
        ('SPECIFIC', _("Specific")),
        ('WEEKLY', _("Weekly")),
    )

    FREQUENCY_INTERVAL_OPTIONS = (
        (0, _("Interval unused")),
        (1, _("Monday")),
        (2, _("Tuesday")),
        (3, _("Wednesday")),
        (4, _("Thursday")),
        (5, _("Friday")),
        (6, _("Saturday")),
        (7, _("Sunday")),
        (7, _("Sunday")),
    )

    schedule_item_type = models.CharField(max_length=50, choices=SCHEDULE_ITEM_TYPES)
    frequency_type = models.CharField(max_length=50, choices=FREQUENCY_TYPES)
    frequency_interval = models.PositiveSmallIntegerField(choices=FREQUENCY_INTERVAL_OPTIONS)
    organization_location_room = models.ForeignKey(OrganizationLocationRoom, on_delete=models.CASCADE)
    organization_classtype = models.ForeignKey(OrganizationClasstype, on_delete=models.CASCADE, null=True)
    organization_level = models.ForeignKey(OrganizationLevel, on_delete=models.CASCADE, null=True)
    date_start = models.DateField()
    date_end = models.DateField(default=None, null=True)
    time_start = models.TimeField()
    time_end = models.TimeField()
    display_public = models.BooleanField(default=False)
    organization_classpass_groups = models.ManyToManyField(
        OrganizationClasspassGroup, 
        through='ScheduleItemOrganizationClasspassGroup', 
        related_name='classpass_groups'
    )
    organization_subscription_groups = models.ManyToManyField(
        OrganizationSubscriptionGroup, 
        through='ScheduleItemOrganizationSubscriptionGroup', 
        related_name='subscription_groups'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.schedule_item_type + ' [' + str(self.date_start) + ']'
    
