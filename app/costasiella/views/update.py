from django.http import Http404, HttpResponse
from django.utils.translation import gettext as _

from ..models import SystemMailTemplate
from ..dudes import PermissionDude, SystemSettingDude, VersionDude


def update(request):
    """
    Update function
    """
    if not request.user:
        raise Http404(_("Page not found..."))

    # Fetch current version
    version_dude = VersionDude()
    current_version = float(version_dude.version)

    # compare version update
    if current_version <= 0.2:
        print('updating to 0.2')

    if current_version < 2021.02:
        _update_to_2021_02()

    if current_version < 2021.03:
        _update_to_2021_03()

    # Set latest version
    new_version = version_dude.update_version()
    # Ensure default permissions are in place
    permission_dude = PermissionDude()
    permission_dude.verify_system_permissions()

    return HttpResponse(
        _("Updated database to version: %s.%s" % (new_version['version'], new_version['version_patch']))
    )


def _update_to_2021_02():
    """
    Update to 2021.02
    :return: None
    """
    # Set default value for 'workflow_shop_subscription_payment_method' if not already set
    setting_dude = SystemSettingDude()
    setting_dude.safe_set(
        'workflow_shop_subscription_payment_method',
        'MOLLIE'
    )


def _update_to_2021_03():
    """
    Update to 2021.03
    :return: None
    """
    system_mail_template = SystemMailTemplate(
        id=110000,
        name="trialpass_followup",
        subject="Trialpass followup",
        title="Trialpass followup",
        description="",
        content="Dear {{account.first_name}}, <br><br> -- Please replace this text with your own to follow up on trial passes. --",
        comments=""
    )
    system_mail_template.save()
