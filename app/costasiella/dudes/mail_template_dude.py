import os
from django.conf import settings
from django.template.loader import render_to_string
from django.template import Template, Context


from django.utils.translation import gettext as _
from django.core.mail import send_mail

from ..models import SystemMailTemplate
from ..dudes.app_settings_dude import AppSettingsDude

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
        self.app_settings_dude = AppSettingsDude()
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
            "class_info_mail": self._render_class_info_mail,
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

    def _render_class_info_mail(self):
        """
        Render info mail for a class
        :return: HTML message
        """
        # Check if we have the required arguments
        schedule_item = self.kwargs.get('schedule_item', None)
        schedule_item_weekly_otc = self.kwargs.get('schedule_item_weekly_otc', None)
        date = self.kwargs.get('date', None)

        if date is None:
            raise Exception(_("date is a required parameter for the class_info_mail template render function"))

        if schedule_item is None or schedule_item_weekly_otc is None:
            raise Exception(_("schedule_item and schedule_item_weekly_otc should be specified"))

        print(schedule_item)
        print(schedule_item_weekly_otc)
        print(date)

        # Fetch template
        mail_template = SystemMailTemplate.objects.get(pk=30000)

        class_time = schedule_item.time_start
        classtype = schedule_item.organization_classtype.name
        location = schedule_item.organization_location_room.school_location.name
        mail_content = schedule_item.info_mail_content

        if schedule_item_weekly_otc:
            if schedule_item_weekly_otc.time_start:
                class_time = schedule_item_weekly_otc.time_start

            if schedule_item_weekly_otc.organization_classtype:
                classtype = schedule_item_weekly_otc.classtype.name

            if schedule_item_weekly_otc.organization_location_room:
                location = schedule_item_weekly_otc.organization_location_room.school_location.name

            if schedule_item_weekly_otc.info_mail_content:
                mail_content = schedule_item_weekly_otc.info_mail_content

        # Render description
        description_context = Context({
            "class_date": date.strftime(self.app_settings_dude.date_format),
            "class_time": class_time.strftime(self.app_settings_dude.time_format),
            "classtype": classtype,
            "location": location
        })
        description_template = Template(mail_template.description)
        description = description_template.render(description_context)

        # Render content
        content_context = Context({
            "mail_content": mail_content
        })
        content_template = Template(mail_template.content)
        content = content_template.render(content_context)

        return dict(
            subject=mail_template.subject,
            title=mail_template.title,
            description=description,
            content=content,
            comments=mail_template.comments
        )

    def _render_template_order_received(self):
        """
        Render order received template
        :return: HTML message
        """
        # Check if we have the required arguments
        finance_order = self.kwargs.get('finance_order', None)

        # Throw a spectacular error if finance_order is not found :)
        if not finance_order:
            raise Exception(_("Finance order not found!"))

        print(finance_order)
        print(finance_order.items)

        # Fetch template
        mail_template = SystemMailTemplate.objects.get(pk=50000)

        # Render template items
        description_context = Context({
            "order": finance_order,
            "order_date": finance_order.created_at.strftime(
                self.app_settings_dude.date_format
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
