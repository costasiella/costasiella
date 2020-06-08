import os
from django.conf import settings
from django.template.loader import render_to_string
from django.template import Template, Context


from django.utils.translation import gettext as _
from django.core.mail import send_mail

from ..models import AppSettings, SystemMailTemplate

# https://docs.djangoproject.com/en/2.2/topics/email/


class MailTemplateDude:
    def __init__(self, email_template, **kwargs):
        """
        :param email_template: field "name" in SystemMailTemplate model
        :param kwargs: one or more of
        - finance_order
        """
        self.email_template = email_template
        self.kwargs = kwargs
        self.app_settings = AppSettings.objects.get(pk=1)
        self.template_default = 'mail/default.html'
        self.template_order_items = 'mail/order_items.html'

        # Read default mail template
        print(settings.BASE_DIR)
        # template_default = os.path.join(
        #     settings.BASE_DIR,
        #     'templates',
        #     'mail',
        #     'default.html'
        # )

        # self.base_template = loader.get_template()

    def render(self):
        """
        Switch render functions and return render function output
        :return: HTML message
        """
        functions = {
            "order_received": self._render_template_order_received
        }

        func = functions.get(self.email_template, lambda: None)
        content = func()
        if content is None:
            return "Invalid Template"

        footer = ""
        footer_template = SystemMailTemplate.objects.get(pk=100000)
        if footer_template:
            footer = footer_template.content

        # Render base template
        context = {
            "logo": "",
            "title": content.get("title", ""),
            "description": content.get("description", ""),
            "content": content.get("content", ""),
            "comments": content.get("comments", ""),
            "footer": footer
        }

        html_message = render_to_string(
            self.template_default,
            context
        )

        return dict(
            subject=content['subject'],
            html_message=html_message
        )

    def _render_template_order_received(self):
        """
        Render order received template
        :return: HTML message
        """
        # Check if we have the required arguments
        finance_order = self.kwargs.get('finance_order', None)

        # Throw a spectacular error if finance_order is not found :)
        print(finance_order)
        print(finance_order.items)

        # Fetch template
        mail_template = SystemMailTemplate.objects.get(pk=50000)

        # Render template items
        description_context = Context({
            "order": finance_order,
            "order_date": finance_order.created_at.strftime(
                self.app_settings.date_format
            )
        })
        description_template = Template(mail_template.description)
        description = description_template.render(description_context)

        # Render content (items table)
        items_context = {
            "order": finance_order,
            "currency_symbol": "€"
        }
        items = render_to_string(
            self.template_order_items,
            items_context
        )
        content_context = Context({
            "order": finance_order,
            "order_items": items
        })
        content_template = Template(mail_template.content)
        content = content_template.render(content_context)

        #TODO: Add footer template

        # print(items_html)

        # t = Template("My name is {{ my_name }}.")
        # c = Context({"my_name": "Adrian"})
        # t.render(c)

        return dict(
            subject=mail_template.subject,
            title=mail_template.title,
            description=description,
            content=content,
            comments=mail_template.comments
        )
