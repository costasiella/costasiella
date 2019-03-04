import factory

from .. import models

class SchoolLocationFactory(factory.Factory):
    class Meta:
        model = models.SchoolLocation

    archived = False
    display_public = True
    name = 'First location'