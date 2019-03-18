from django.db import models

class FinanceGlAccount(models.Model):
    archived = models.BooleanField(default=False)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
