import factory

from .. import models
from django.contrib.auth import get_user_model

class SchoolLocationFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.SchoolLocation

    archived = False
    display_public = True
    name = 'First location'


class AdminFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()
    # FACTORY_FOR = get_user_model()

    email = 'admin@costasiellla.com'
    username = 'admin'
    first_name = 'admin'
    last_name = 'user (the boss)'
    password = factory.PostGenerationMethodCall('set_password', 'CSAdmin1#')

    is_superuser = True
    is_staff = True
    is_active = True
