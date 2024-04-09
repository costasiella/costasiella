from django.utils.translation import gettext as _
from django.conf import settings


class CountryDude:
    @staticmethod
    def iso_country_code_to_name(iso_country_code):
        """
        Return the country name from an ISO country code
        :return: string - Country name
        """
        country_name = _("Not found")

        for country in settings.ISO_COUNTRY_CODES:
            if country['Code'] == iso_country_code:
                country_name = country['Name']

        return country_name
