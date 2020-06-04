from django.http import Http404, HttpResponse
from django.utils.translation import gettext as _

from ..dudes.setup_dude import SetupDude


def setup(request):
    """
    Setup function
    """
    # Execute setup
    setup_dude = SetupDude()
    message = setup_dude.setup()

    return HttpResponse(message)
