import os
from django.conf import settings
from django.template.loader import render_to_string

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
        self.default_template = 'mail/default.html'

        # Read default mail template
        print(settings.BASE_DIR)
        # default_template = os.path.join(
        #     settings.BASE_DIR,
        #     'templates',
        #     'mail',
        #     'default.html'
        # )

        # self.base_template = loader.get_template()

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

        # Render content

        # Render template
        context = {
            "logo": "",
            "title": "title",
            "description": "description",
            "content": "hello world",
            "comments": "comments",
            "footer": "footer"
        }

        html_message = render_to_string(
            self.default_template,
            context
        )

        return dict(
            subject=_("Order received"),
            html_message=html_message
        )
