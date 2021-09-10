from django.utils.translation import gettext as _


class Messages:
    finance_invoice_belongs_other_account = _("This invoice doesn't belong to your account.")
    finance_order_belongs_other_account = _("This order doesn't belong to your account.")
    user_permission_denied = _("Permission denied!")
    user_invalid_order_status = _("Invalid order status. Allowed status: 'CANCELLED'")
    user_not_logged_in = _("Not logged in!")
