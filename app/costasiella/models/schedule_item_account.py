from django.utils.translation import gettext as _

from django.db import models


from .schedule_item import ScheduleItem
from .account import Account
from .choices.instructor_roles import get_instructor_roles
from .helpers import model_string


# Create your models here.
class ScheduleItemAccount(models.Model):
    INSTRUCTOR_ROLES = get_instructor_roles()

    schedule_item = models.ForeignKey(ScheduleItem, on_delete=models.CASCADE,
                                      related_name="instructors")
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    role = models.CharField(default="", max_length=50, choices=INSTRUCTOR_ROLES)
    account_2 = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, related_name="account_2")
    role_2 = models.CharField(default="", max_length=50, choices=INSTRUCTOR_ROLES)
    date_start = models.DateField()
    date_end = models.DateField(default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return model_string(self)
