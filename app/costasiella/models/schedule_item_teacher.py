from django.utils.translation import gettext as _

from django.db import models


from .schedule_item import ScheduleItem
from .account import Account

# Create your models here.

class ScheduleItemTeacher(models.Model):
    TEACHER_ROLES = [
        ['', _("Regular")],
        ['SUB', _("Subteacher")],
        ['ASSISTANT', _("Assistant")],
        ['KARMA', _("Karma")]
    ]

    schedule_item = models.ForeignKey(ScheduleItem, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=TEACHER_ROLES)
    account_2 = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, related_name="account_2")
    role_2 = models.CharField(default="", max_length=50, choices=TEACHER_ROLES)
    date_start = models.DateField()
    date_end = models.DateField(default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.schedule_item + ' [' + self.account.full_name + " - " + str(date_start) + ']'
    
