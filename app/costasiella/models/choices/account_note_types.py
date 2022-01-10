from django.utils.translation import gettext as _


def get_account_note_types():
    return (
        ('BACKOFFICE', _("Backoffice")),
        ('INSTRUCTORS', _("Instructors")),
    )
