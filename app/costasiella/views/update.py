from django.http import Http404, HttpResponse
from django.utils.translation import gettext as _

from ..dudes.version_dude import VersionDude


def update(request):
    """
    Update function

    :param: POST: node_id - FinanceInvoiceNode ID
    """
    if not request.user:
        raise Http404(_("Page not found..."))

    # Fetch current version
    version_dude = VersionDude()
    current_version = float(version_dude.version)

    # compare version update
    if current_version <= 0.02:
        print('updating to 0.02')

    # Set latest version
    new_version = version_dude.update_version()

    return HttpResponse(
        _("Updated database to version: %s.%s" % (new_version['version'], new_version['version_patch']))
    )
