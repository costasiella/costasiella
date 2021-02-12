from django.utils.translation import gettext as _

from django.db import models

from .account import Account
from .finance_costcenter import FinanceCostCenter
from .finance_glaccount import FinanceGLAccount
from .finance_tax_rate import FinanceTaxRate
from .organization_appointment import OrganizationAppointment


class OrganizationAppointmentPrice(models.Model):
    class Meta:
        unique_together = ('account', 'organization_appointment',)

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    organization_appointment = models.ForeignKey(OrganizationAppointment, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    finance_tax_rate = models.ForeignKey(FinanceTaxRate, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return self.organization_appointment.name + ' ' + self.account.full_name + ' - ' + self.price
    