from django.db import models
from .organization_appointment_category import OrganizationAppointmentCategory

# Create your models here.

class OrganizationAppointment(models.Model):
    organization_appointment_category = models.ForeignKey(OrganizationAppointmentCategory, on_delete=models.CASCADE)
    archived = models.BooleanField(default=False)
    display_public = models.BooleanField(default=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.organization_appointment_category.name + ' ' + 'Appointment' + ': ' + self.name
    
