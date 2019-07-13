from django.db import models

from .schedule_item import ScheduleItem
from .organization_subscription_group import OrganizationSubscriptionGroup

class ScheduleItemOrganizationSubscriptionGroup(models.Model):
    schedule_item = models.ForeignKey(ScheduleItem, on_delete=models.CASCADE)
    organization_subscription_group = models.ForeignKey(OrganizationSubscriptionGroup, on_delete=models.CASCADE)
    enroll = models.Boolean(default=False)
    shop_book = models.Boolean(default=False)
    attend = models.Boolean(default=False)
    

    def __str__(self):
        return self.organization_subscription_group.name + " schedule item " + str(self.schedule_item.id)
    
