from django.utils.translation import gettext as _


def get_instructor_roles():
    return [
        ['', _("Regular")],
        ['SUB', _("Substitute")],
        ['ASSISTANT', _("Assistant")],
        ['KARMA', _("Karma")]
    ]
