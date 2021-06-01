from django.utils.translation import gettext as _

from django.db import models

from .schedule_event import ScheduleEvent
from .helpers import model_string


class ScheduleEventEarlybird(models.Model):
    schedule_event = models.ForeignKey(ScheduleEvent, on_delete=models.CASCADE, related_name="earlybirds")
    date_start = models.DateField()
    date_end = models.DateField()
    discount_percentage = models.DecimalField(max_digits=20, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return model_string(self)
