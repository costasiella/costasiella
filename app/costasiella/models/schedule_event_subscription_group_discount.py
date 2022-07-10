from django.utils.translation import gettext as _

from django.db import models

from .organization_subscription_group import OrganizationSubscriptionGroup
from .schedule_event import ScheduleEvent
from .helpers import model_string


class ScheduleEventSubscriptionGroupDiscount(models.Model):
    schedule_event = models.ForeignKey(ScheduleEvent, on_delete=models.CASCADE)
    organization_subscription_group = models.ForeignKey(OrganizationSubscriptionGroup,
                                                        on_delete=models.CASCADE)
    discount_percentage = models.DecimalField(max_digits=20, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return model_string(self)
