from django.utils.translation import gettext as _
from django.conf import settings


def get_account_country_codes():
    country_codes = []
    for country in settings.ISO_COUNTRY_CODES:
        country_codes.append([country['Code'], country['Name']])

    return country_codes
