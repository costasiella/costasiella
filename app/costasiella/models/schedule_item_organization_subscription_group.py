from django.db import models

from .schedule_item import ScheduleItem
from .organization_subscription_group import OrganizationSubscriptionGroup


class ScheduleItemOrganizationSubscriptionGroup(models.Model):
    schedule_item = models.ForeignKey(ScheduleItem, on_delete=models.CASCADE)
    organization_subscription_group = models.ForeignKey(OrganizationSubscriptionGroup, on_delete=models.CASCADE)
    enroll = models.BooleanField(default=False)
    shop_book = models.BooleanField(default=False)
    attend = models.BooleanField(default=False)

    def __str__(self):
        return self.organization_subscription_group.name + " schedule item " + str(self.schedule_item.id)
