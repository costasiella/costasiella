from django.utils.translation import gettext as _


def get_account_genders():
    return [
        ['', _("")],
        ['F', _("Female")],
        ['M', _("Male")],
        ['X', _("Other")]
    ]
