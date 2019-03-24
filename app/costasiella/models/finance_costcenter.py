from django.db import models

class FinanceCostCenter(models.Model):
    archived = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255, default="")

    def __str__(self):
        return self.name
    
