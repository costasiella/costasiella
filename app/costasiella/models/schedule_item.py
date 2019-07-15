from django.utils.translation import gettext as _

from django.db import models


from .organization_classtype import OrganizationClasstype
from .organization_location_room import OrganizationLocationRoom
from .organization_level import OrganizationLevel
from .organization_subscription_group import OrganizationSubscriptionGroup

# Create your models here.

class ScheduleItem(models.Model):
    class Meta:
        permissions = [
            ('view_scheduleclass', _("Can view schedule class")),
            ('add_scheduleclass', _("Can add schedule class")),
            ('change_scheduleclass', _("Can change schedule class")),
            ('delete_scheduleclass', _("Can delete schedule class")),
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
    organization_subscription_groups = models.ManyToManyField(
        OrganizationSubscriptionGroup, 
        through='ScheduleItemOrganizationSubscriptionGroup', 
        related_name='subscription_groups'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.schedule_item_type + ' [' + str(self.date_start) + ']'
    


# def define_schedule():
#     schedule_types = [
#         ('appointment', T("Appointment"))
#     ]

#     schedule_frequency_types = [
#         ('specific', T("Specific")),
#         ('weekly', T("Weekly")),
#     ]

#     schedule_frequency_interval_options = [
#         (0, T("Interval Unused")),
#         (1, T("Monday")),
#         (2, T("Tuesday")),
#         (3, T("Wednesday")),
#         (4, T("Thursday")),
#         (5, T("Friday")),
#         (6, T("Saturday")),
#         (7, T("Sunday")),
#     ]

#     db.define_table('schedule',
#         Field('ScheduleType',
#               readable=False,
#               writable=False,
#               requires=IS_IN_SET(schedule_types),
#               default='appointment'),
#         Field('FrequencyType',
#               readable=False,
#               writable=False,
#               requies=IS_IN_SET(schedule_frequency_types),
#               default='weekly'),
#         Field('FrequencyInterval', 'integer',
#               readable=False,
#               writable=False,
#               requies=IS_IN_SET(schedule_frequency_interval_options),
#               default=0),
#         Field('school_locations_id', db.school_locations,
#               label=T("Location")),
#         Field('Startdate', 'date', required=True,
#               requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
#                                         minimum=datetime.date(1900, 1, 1),
#                                         maximum=datetime.date(2999, 1, 1)),
#               represent=represent_date,
#               label=T("Start date"),
#               widget=os_datepicker_widget),
#         Field('Enddate', 'date',
#               requires=IS_EMPTY_OR(IS_DATE_IN_RANGE(format=DATE_FORMAT,
#                                                     minimum=datetime.date(1900, 1, 1),
#                                                     maximum=datetime.date(2999, 1, 1))),
#               represent=represent_date,
#               label=T("End date"),
#               widget=os_datepicker_widget),
#         Field('Starttime', 'time', required=True,
#               requires=IS_TIME(error_message='must be HH:MM'),
#               represent=lambda value, row: value.strftime('%H:%M') if value else '',
#               # widget=os_gui.get_widget_time,
#               label=T("Start time"),
#               widget=os_time_widget),
#         Field('Endtime', 'time', required=True,
#               requires=IS_TIME(error_message='must be HH:MM'),
#               represent=lambda value, row: value.strftime('%H:%M') if value else '',
#               widget=os_time_widget,
#               label=T("End time")),
#         Field('AllowAPI', 'boolean',
#             default=False,
#             label=T("Public"),
#             comment=T("When the API is in use, this checkbox defines whether \
#                 an item is passed to the website.")),
#     )
