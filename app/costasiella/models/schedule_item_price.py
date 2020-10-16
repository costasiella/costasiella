from django.utils.translation import gettext as _

from django.db import models


from .schedule_item import ScheduleItem
from .organization_classpass import OrganizationClasspass


# Create your models here.
class ScheduleItemPrice(models.Model):

    schedule_item = models.ForeignKey(ScheduleItem, on_delete=models.CASCADE)
    organization_classpass_dropin = models.ForeignKey(
        OrganizationClasspass, on_delete=models.CASCADE, null=True, related_name="organizationclasspassesdropin")
    organization_classpass_trial = models.ForeignKey(
        OrganizationClasspass, on_delete=models.CASCADE, null=True, related_name="organizationclasspassestrial")
    date_start = models.DateField()
    date_end = models.DateField(default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.schedule_item) + ' [' + str(self.date_start) + " - " + str(self.date_end) + ']'
