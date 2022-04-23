import datetime

from django.db import models
from django.utils import timezone

from .helpers import model_string


class InsightAccountInactive(models.Model):
    no_activity_after_date = models.DateField(default=timezone.now().date() - datetime.timedelta(days=365))
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return model_string(self)
