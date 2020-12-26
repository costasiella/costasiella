from django.db import models
from sorl.thumbnail import ImageField

from .schedule_event import ScheduleEvent


# Create your models here.
class ScheduleEventMedia(models.Model):
    schedule_event = models.ForeignKey(ScheduleEvent, on_delete=models.CASCADE)
    sort_order = models.PositiveIntegerField(default=0)
    description = models.TextField()
    image = ImageField(upload_to='schedule_event_media', default=None)

    def __str__(self):
        return self.schedule_event.name + ' media [ %s ]' % self.sort_order
