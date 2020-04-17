from django.utils.translation import gettext as _
from django.core.mail import send_mail

# https://docs.djangoproject.com/en/2.2/topics/email/


class MailTemplateDude:
    def __init__(self, email_template, **kwargs):
        """
        :param kwargs:
        """
        self.email_template = email_template
        self.kwargs = kwargs
        # self.finance_order = kwargs.get('finance_order', None)

    def render(self):
        """
        Render email template
        :param email_template: field "name" in SystemMailTemplate model
        :return: HTML message
        """
        functions = {
            "order_received": self._render_template_order_received
        }

        func = functions.get(self.email_template, lambda: "Invalid Template")

        return func()

    def _render_template_order_received(self):
        """
        Render order received template
        :return: HTML message
        """
        # Fetch template

        # Check if we have the required arguments
        finance_order = self.kwargs.get('finance_order', None)

        # Throw a spectacular error if finance_order is not found :)
        print(finance_order)

        return dict(
            subject="order received",
            html_message="<html>Hello world from order received template</html>"
        )

        # Fetch template here
