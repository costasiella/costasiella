from django.utils.translation import gettext as _

from django.db import models

from .account import Account
from .organization_classtype import OrganizationClasstype
from .organization_location_room import OrganizationLocationRoom
from .organization_level import OrganizationLevel
from .organization_classpass_group import OrganizationClasspassGroup
from .organization_subscription_group import OrganizationSubscriptionGroup
from .schedule_event import ScheduleEvent

from .choices.teacher_roles import get_teacher_roles
from .choices.schedule_item_otc_statuses import get_schedule_item_otc_statuses
from .choices.schedule_item_frequency_types import get_schedule_item_frequency_types


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

    FREQUENCY_TYPES = get_schedule_item_frequency_types()

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

    TEACHER_ROLES = get_teacher_roles()
    STATUSES = get_schedule_item_otc_statuses()

    schedule_event = models.ForeignKey(ScheduleEvent, on_delete=models.CASCADE, null=True)
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
    info_mail_content = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ################ BEGIN EMPTY FIELDS ################
    # No value is actually stored here for now, but these fields are very useful in the schedule_class schema
    # By having these fields here we can map the schedule_item_teacher or schedule_item_weekly_otc account 
    # into these fields
    ####################################################
    status = models.CharField(max_length=255, default="", choices=STATUSES)
    description = models.CharField(max_length=255, default="")
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="si_account")
    role = models.CharField(default="", max_length=50, choices=TEACHER_ROLES)
    account_2 = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="si_account_2")
    role_2 = models.CharField(default="", max_length=50, choices=TEACHER_ROLES)
    ################ END EMPTY FIELDS ##################

    def __str__(self):
        return self.schedule_item_type + ' [' + str(self.date_start) + ']'
