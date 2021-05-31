from django.utils.translation import gettext as _


def get_organization_document_types():
    return [
        ['TERMS_AND_CONDITIONS', _("Terms and conditions")],
        ['PRIVACY_POLICY', _("Privacy policy")],
    ]
