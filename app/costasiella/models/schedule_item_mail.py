from django.db import models

from .schedule_item import ScheduleItem

from .choices.schedule_item_frequency_types import get_schedule_item_frequency_types


class ScheduleItemMail(models.Model):
    FREQUENCY_TYPES = get_schedule_item_frequency_types()

    schedule_item = models.ForeignKey(ScheduleItem, on_delete=models.CASCADE)
    frequency_type = models.CharField(max_length=50, choices=FREQUENCY_TYPES)
    date = models.DateField(null=True)
    mail_content = models.TextField()

    def __str__(self):
        return "schedule item mail " + str(self.schedule_item.id) + "[ %s ]: " % str(self.date) + self.mail_content
