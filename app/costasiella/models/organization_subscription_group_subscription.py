from django.db import models

from .organization_subscription import OrganizationSubscription
from .organization_subscription_group import OrganizationSubscriptionGroup


class OrganizationSubscriptionGroupSubscription(models.Model):
    organization_subscription_group = models.ForeignKey(OrganizationSubscriptionGroup, on_delete=models.CASCADE)
    organization_subscription = models.ForeignKey(OrganizationSubscription, on_delete=models.CASCADE)

    def __str__(self):
        return self.organization_subscription_group.name + ' ' + self.organization_subscription.name
