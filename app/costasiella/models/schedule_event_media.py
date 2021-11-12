from django.db import models
from sorl.thumbnail import ImageField

from .helpers import model_string
from .schedule_event import ScheduleEvent


# Create your models here.
class ScheduleEventMedia(models.Model):
    schedule_event = models.ForeignKey(ScheduleEvent, on_delete=models.CASCADE, related_name="media")
    sort_order = models.PositiveIntegerField(default=0)
    description = models.CharField(max_length=255)
    image = ImageField(upload_to='schedule_event_media', default=None)

    def __str__(self):
        return model_string(self)
