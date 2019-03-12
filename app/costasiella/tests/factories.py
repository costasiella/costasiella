import factory

from .. import models
from django.contrib.auth import get_user_model

class SchoolLocationFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.SchoolLocation

    archived = False
    display_public = True
    name = "First location"


class SchoolClasstypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.SchoolClasstype

    archived = False
    display_public = True
    name = "First classtype"
    description = "Classtype description"
    url_website = "http://www.costasiella.com"


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


class RegularUserFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()
    # FACTORY_FOR = get_user_model()

    email = 'user@costasiellla.com'
    username = 'user'
    first_name = 'user'
    last_name = 'regular user'
    password = factory.PostGenerationMethodCall('set_password', 'CSUser!1#')

    is_active = True
