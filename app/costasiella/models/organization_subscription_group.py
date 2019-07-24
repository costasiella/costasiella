from django.db import models

from .organization_subscription import OrganizationSubscription

class OrganizationSubscriptionGroup(models.Model):
    archived = models.BooleanField(default=False)
    name = models.CharField(max_length=255, unique=True)
    organization_subscriptions = models.ManyToManyField(
        OrganizationSubscription, 
        through='OrganizationSubscriptionGroupSubscription', 
        related_name='subscriptions'
    )

    def __str__(self):
        return self.name
        
