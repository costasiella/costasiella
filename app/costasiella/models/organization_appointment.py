from django.db import models


from .organization_appointment_category import OrganizationAppointmentCategory
from .finance_costcenter import FinanceCostCenter
from .finance_glaccount import FinanceGLAccount

# Create your models here.

class OrganizationAppointment(models.Model):
    organization_appointment_category = models.ForeignKey(OrganizationAppointmentCategory, on_delete=models.CASCADE)
    archived = models.BooleanField(default=False)
    display_public = models.BooleanField(default=True)
    name = models.CharField(max_length=255)
    finance_glaccount = models.ForeignKey(FinanceGLAccount, on_delete=models.SET_NULL, null=True)
    finance_costcenter = models.ForeignKey(FinanceCostCenter, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.organization_appointment_category.name + ' ' + 'Appointment' + ': ' + self.name
    
