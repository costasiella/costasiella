from django.db import models

# Create your models here.

class OrganizationAppointmentCategory(models.Model):
    archived = models.BooleanField(default=False)
    display_public = models.BooleanField(default=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
