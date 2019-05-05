from django.contrib.auth.models import AbstractUser
from django.db import models

class Account(AbstractUser):
    # add additional fields in here

    trashed = models.BooleanField(default=False)
    # teacher and employee will use OneToOne fields. An account can optionally be a teacher or employee.

    def __str__(self):
        return self.email