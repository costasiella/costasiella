from django.utils.translation import gettext as _

from django.db import models


class OrganizationAppointment(models.Model):
    archived = models.BooleanField(default=False)
    display_public = models.BooleanField(default=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    url_website = models.URLField()
    image = ImageField(upload_to='organization_appointment_images', default=None)

    def __str__(self):
        return self.name
    
