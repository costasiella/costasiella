from django.db import models


class FinanceGLAccount(models.Model):
    archived = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    code = models.IntegerField(default=0)

    def __str__(self):
        return self.name
