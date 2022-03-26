from django.db import models

from .helpers import model_string


class SystemMailChimpList(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    frequency = models.CharField(max_length=255)
    mailchimp_list_id = models.CharField(max_length=255)

    def __str__(self):
        return model_string(self)
