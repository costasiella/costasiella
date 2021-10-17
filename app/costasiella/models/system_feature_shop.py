from django.utils.translation import gettext as _
from django.db import models

from .helpers import model_string


class SystemFeatureShop(models.Model):
    memberships = models.BooleanField(default=False)
    subscriptions = models.BooleanField(default=False)
    classpasses = models.BooleanField(default=False)
    classes = models.BooleanField(default=False)
    events = models.BooleanField(default=False)
    account_data_download = models.BooleanField(default=True)

    def __str__(self):
        return model_string(self)
