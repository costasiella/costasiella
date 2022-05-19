import datetime

from django.db import models
from django.utils import timezone

from .helpers import model_string


class InsightAccountInactive(models.Model):
    no_activity_after_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return model_string(self)
