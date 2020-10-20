from django.utils.translation import gettext as _

from django.db import models

from .schedule_event import ScheduleEvent
from .finance_tax_rate import FinanceTaxRate
from .finance_costcenter import FinanceCostCenter
from .finance_glaccount import FinanceGLAccount


class ScheduleEventTicket(models.Model):
    schedule_event = models.ForeignKey(ScheduleEvent, on_delete=models.CASCADE)
    full_event = models.BooleanField(default=False)
    deletable = models.BooleanField(default=True)
    display_public = models.BooleanField(default=True)
    name = models.CharField(max_length=255)
    description = models.TextField(default="")
    price = models.DecimalField(max_digits=20, decimal_places=2)
    finance_tax_rate = models.ForeignKey(FinanceTaxRate, on_delete=models.CASCADE)
    finance_glaccount = models.ForeignKey(FinanceGLAccount, on_delete=models.CASCADE, null=True)
    finance_costcenter = models.ForeignKey(FinanceCostCenter, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name + ' [' + str(self.price) + ']'