import datetime

from django.utils.translation import gettext as _
from django.utils import timezone
from django.db import models

from .finance_costcenter import FinanceCostCenter
from .finance_glaccount import FinanceGLAccount
from .finance_order import FinanceOrder
from .finance_tax_rate import FinanceTaxRate
from .organization_classpass import OrganizationClasspass
from .organization_subscription import OrganizationSubscription
from .schedule_event_ticket import ScheduleEventTicket
from .schedule_item import ScheduleItem
from .choices.schedule_item_attendance_types import get_schedule_item_attendance_types

now = timezone.now()


class FinanceOrderItem(models.Model):
    ATTENDANCE_TYPES = get_schedule_item_attendance_types()

    finance_order = models.ForeignKey(FinanceOrder, on_delete=models.CASCADE, related_name="items")
    # Event ticket fields
    schedule_event_ticket = models.ForeignKey(ScheduleEventTicket, on_delete=models.CASCADE, null=True)
    # Subscription fields
    organization_subscription = models.ForeignKey(OrganizationSubscription, on_delete=models.CASCADE, null=True)
    # Class pass fields
    organization_classpass = models.ForeignKey(OrganizationClasspass, on_delete=models.CASCADE, null=True)
    # Class fields
    attendance_type = models.CharField(max_length=255, choices=ATTENDANCE_TYPES, null=True)
    attendance_date = models.DateField(null=True)
    schedule_item = models.ForeignKey(ScheduleItem, on_delete=models.CASCADE, null=True)
    # General fields
    product_name = models.CharField(max_length=255)
    description = models.TextField(default="")
    quantity = models.DecimalField(max_digits=20, decimal_places=2)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    finance_tax_rate = models.ForeignKey(FinanceTaxRate, on_delete=models.SET_NULL, null=True)
    subtotal = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    finance_glaccount = models.ForeignKey(FinanceGLAccount, on_delete=models.SET_NULL, null=True)
    finance_costcenter = models.ForeignKey(FinanceCostCenter, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return _("Order: ") + str(self.id) + self.product_name

    def save(self, *args, **kwargs):
        self.subtotal = self._calculate_subtotal()
        self.tax = self._calculate_tax()
        self.total = self._calculate_total()

        super(FinanceOrderItem, self).save(*args, **kwargs)

    def _calculate_subtotal(self):
        from ..dudes import FinanceDude
        finance_dude = FinanceDude()
        return finance_dude.calculate_subtotal(
            price=self.price,
            quantity=self.quantity,
            finance_tax_rate=self.finance_tax_rate
        )

    def _calculate_tax(self):
        from ..dudes import FinanceDude
        finance_dude = FinanceDude()
        return finance_dude.calculate_tax(
            subtotal=self.subtotal,
            finance_tax_rate=self.finance_tax_rate
        )

    def _calculate_total(self):
        from ..dudes import FinanceDude
        finance_dude = FinanceDude()
        return finance_dude.calculate_total(
            subtotal=self.subtotal,
            tax=self.tax
        )
