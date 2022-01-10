from django.utils.translation import gettext as _
from django.db import models


from .schedule_item import ScheduleItem
from .account import Account


# Create your models here.
class ScheduleItemInstructorAvailable(models.Model):
    schedule_item = models.ForeignKey(ScheduleItem, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    date_start = models.DateField()
    date_end = models.DateField(default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.schedule_item + ' available [' + self.account.full_name + " - " + str(self.date_start) + ']'
