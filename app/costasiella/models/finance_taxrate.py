from django.db import models

class FinanceTaxRate(models.Model):
    archived = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    percentage = models.IntegerField()
    code = models.CharField(max_length=255, default="")

    def __str__(self):
        return self.name
    
