from django.utils.translation import gettext as _
from django.db import models

from .schedule_item import ScheduleItem
from .account import Account
from .helpers import model_string

# Create your models here.
class ScheduleItemEmployee(models.Model):
    schedule_item = models.ForeignKey(ScheduleItem, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="employees")
    account_2 = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, related_name="employees_2")
    date_start = models.DateField()
    date_end = models.DateField(default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return model_string(self)
