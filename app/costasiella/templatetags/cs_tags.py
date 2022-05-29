# custom_tags.py
from django import template

register = template.Library()


@register.simple_tag
def cs_email_logo_url():
    """
    Return email logo src if any
    """
    from ..dudes import SystemSettingDude
    from ..models import Organization

    system_setting_dude = SystemSettingDude()
    system_hostname = system_setting_dude.get("system_hostname")

    organization = Organization.objects.get(id=100)

    return "https://" + system_hostname + organization.logo_email.url
