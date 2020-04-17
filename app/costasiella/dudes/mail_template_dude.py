from django.utils.translation import gettext as _
from django.core.mail import send_mail

# https://docs.djangoproject.com/en/2.2/topics/email/


class MailTemplateDude:
    def __init__(self, **kwargs):
        """
        :param kwargs:
        """
        self.finance_order = kwargs.get('finance_order', None)

    def render(self, email_template):
        """
        Render email template
        :param email_template: field "name" in SystemMailTemplate model
        :return: HTML message
        """
        functions = {
            "order_received": self._render_template_order_received
        }

        func = functions.get(email_template, lambda: "Invalid Template")

        return func()

    def _render_template_order_received(self):
        """
        Render order received template
        :return: HTML message
        """
        # Check if we have the required arguments
        print(self.finance_order)

        # Fetch template here
