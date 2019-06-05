from django.utils.translation import gettext as _

from django.db import models

# from .finance_costcenter import FinanceCostCenter
# from .finance_glaccount import FinanceGLAccount
# from .finance_taxrate import FinanceTaxRate
# Create your models here.

class Schedule(models.Model):
    # VALIDITY_UNITS = (
    #     ("DAYS", _("Days")),
    #     ("WEEKS", _("Weeks")),
    #     ("MONTHS", _("Months"))
    # )

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

    date_start = models.DateField()
    date_end = models.DateField(null=True)

    # archived = models.BooleanField(default=False)
    # display_public = models.BooleanField(default=True)
    # display_shop = models.BooleanField(default=True)
    # name = models.CharField(max_length=255)
    # description = models.CharField(max_length=255)
    # price = models.DecimalField(max_digits=20, decimal_places=2)
    # finance_tax_rate = models.ForeignKey(FinanceTaxRate, on_delete=models.CASCADE)
    # validity = models.PositiveIntegerField()
    # validity_unit = models.CharField(max_length=10, choices=VALIDITY_UNITS, default="DAYS")
    # terms_and_conditions = models.TextField()
    # finance_glaccount = models.ForeignKey(FinanceGLAccount, on_delete=models.CASCADE, null=True)
    # finance_costcenter = models.ForeignKey(FinanceCostCenter, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name
    





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
