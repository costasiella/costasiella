from django.db import models

from .schedule_item import ScheduleItem
from .organization_classpass_group import OrganizationClasspassGroup


class ScheduleItemOrganizationClasspassGroup(models.Model):
    schedule_item = models.ForeignKey(ScheduleItem, on_delete=models.CASCADE)
    organization_classpass_group = models.ForeignKey(OrganizationClasspassGroup, on_delete=models.CASCADE)
    shop_book = models.BooleanField(default=False)
    attend = models.BooleanField(default=False)

    def __str__(self):
        return self.organization_classpass_group.name + " schedule item " + str(self.schedule_item.id)
