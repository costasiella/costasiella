from django.utils.translation import gettext as _

def get_teacher_roles():
    return  [
        ['', _("Regular")],
        ['SUB', _("Subteacher")],
        ['ASSISTANT', _("Assistant")],
        ['KARMA', _("Karma")]
    ]