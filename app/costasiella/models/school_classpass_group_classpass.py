from django.db import models

from .school_classpass import SchoolClasspass
from .school_classpass_group import SchoolClasspassGroup

class SchoolClasspassGroupClasspass(models.Model):
    school_classpass = models.ForeignKey(SchoolClasspass, on_delete=models.CASCADE)
    school_classpass_group = models.ForeignKey(SchoolClasspassGroup, on_delete=models.CASCADE)

    def __str__(self):
        return self.school_classpass_group.Name + ' ' + self.school_classpass.Name
    
