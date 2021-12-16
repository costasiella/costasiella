import os
from django.conf import settings
from django.template.loader import render_to_string
from django.template import Template, Context


from django.utils.translation import gettext as _
from django.core.mail import send_mail

from ..dudes.app_settings_dude import AppSettingsDude

# https://docs.djangoproject.com/en/2.2/topics/email/


class MailTemplateDude:
    def __init__(self, email_template, **kwargs):
        """
        :param email_template: field "name" in SystemMailTemplate model
        :param kwargs: one or more of
        - account
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
        from ..models import SystemMailTemplate

        print("mail template render called")

        functions = {
            "class_info_mail": self._render_class_info_mail,
            "event_info_mail": self._render_event_info_mail,
            "order_received": self._render_template_order_received,
            "recurring_payment_failed": self._render_template_recurring_payment_failed,
            "trialpass_followup": self._render_template_triaplass_followup,
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
        from ..models import SystemMailTemplate, ScheduleItemWeeklyOTC

        # Check if we have the required arguments
        error = False
        error_message = ""

        schedule_item = self.kwargs.get('schedule_item', None)
        date = self.kwargs.get('date', None)

        if date is None:
            raise Exception(_("date is a required parameter for the class_info_mail template render function"))

        if schedule_item is None:
            raise Exception(_("schedule_item should be specified"))

        schedule_item_weekly_otc = None
        qs = ScheduleItemWeeklyOTC.objects.filter(
            schedule_item=schedule_item,
            date=date
        )
        if qs.exists:
            schedule_item_weekly_otc = qs.first()

        # Fetch template
        mail_template = SystemMailTemplate.objects.get(pk=30000)

        class_time = schedule_item.time_start
        classtype = schedule_item.organization_classtype.name
        location = schedule_item.organization_location_room.organization_location.name
        mail_content = schedule_item.info_mail_content

        if schedule_item_weekly_otc:
            if schedule_item_weekly_otc.time_start:
                class_time = schedule_item_weekly_otc.time_start

            if schedule_item_weekly_otc.organization_classtype:
                classtype = schedule_item_weekly_otc.classtype.name

            if schedule_item_weekly_otc.organization_location_room:
                location = schedule_item_weekly_otc.organization_location_room.organization_location.name

            if schedule_item_weekly_otc.info_mail_content:
                mail_content = schedule_item_weekly_otc.info_mail_content

        if not mail_content:
            error = True
            error_message = _("No mail content defined, no need to send a mail.")

        # Render description
        description_context = Context({
            "class_date": date.strftime(self.app_settings_dude.date_format),
            "class_time": class_time.strftime(self.app_settings_dude.time_format),
            "class_classtype": classtype,
            "class_location": location
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
            comments=mail_template.comments,
            error=error,
            error_message=error_message
        )

    def _render_event_info_mail(self):
        """
        Render info mail for an event
        :return: HTML message
        """
        from ..models import SystemMailTemplate

        app_settings_dude = AppSettingsDude()
        # date_dude = DateToolsDude()
        # Check if we have the required arguments
        error = False
        error_message = ""

        account_schedule_event_ticket = self.kwargs.get('account_schedule_event_ticket', None)

        if account_schedule_event_ticket is None:
            raise Exception(
                _("account_schedule_event_ticket is a required parameter \
                for the class_info_mail template render function"))

        schedule_event_ticket = account_schedule_event_ticket.schedule_event_ticket
        schedule_event = schedule_event_ticket.schedule_event

        # Fetch template
        mail_template = SystemMailTemplate.objects.get(name="event_info_mail")
        date_format = app_settings_dude.date_format
        time_format = app_settings_dude.time_format

        schedule_event_time_info = \
            schedule_event.date_start.strftime(date_format) + " " + \
            schedule_event.time_start.strftime(time_format) + " - " + \
            schedule_event.date_end.strftime(date_format) + " " + \
            schedule_event.time_end.strftime(time_format)

        mail_content = schedule_event.info_mail_content

        if not mail_content:
            error = True
            error_message = _("No mail content defined, no need to send a mail.")

        # Render description
        description_context = Context({
            "schedule_event": schedule_event,
            "schedule_event_ticket": schedule_event_ticket,
            "schedule_event_time_info": schedule_event_time_info
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
            comments=mail_template.comments,
            error=error,
            error_message=error_message
        )

    def _render_template_order_received(self):
        """
        Render order received template
        :return: HTML message
        """
        from ..models import SystemMailTemplate
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

    def _render_template_recurring_payment_failed(self):
        """
        Render recurring payment failed template
        :return: HTML message
        """
        from ..models import SystemMailTemplate
        from .system_setting_dude import SystemSettingDude

        system_setting_dude = SystemSettingDude()
        # Check if we have the required arguments
        finance_invoice = self.kwargs.get('finance_invoice', None)

        # Throw a spectacular error if finance_invoice is not found :)
        if not finance_invoice:
            raise Exception(_("Finance invoice not found!"))

        # Fetch template
        mail_template = SystemMailTemplate.objects.get(pk=70000)

        # Render template content
        system_hostname = system_setting_dude.get('system_hostname')
        link_profile_invoices = "https://%s/#/shop/account/invoices" % system_hostname
        content_context = Context({
            "link_profile_invoices": link_profile_invoices
        })
        content_template = Template(mail_template.content)
        content = content_template.render(content_context)

        return dict(
            subject=mail_template.subject,
            title=mail_template.title,
            description=mail_template.description,
            content=content,
            comments=mail_template.comments
        )

    def _render_template_triaplass_followup(self):
        """

        :return:
        """
        from ..models import SystemMailTemplate
        # Check if we have the required arguments, if not raise an exception
        account = self.kwargs.get('account', None)
        if account is None:
            raise Exception(_("account is a required parameter for the trialpass_followup template render function"))

        # Fetch template
        mail_template = SystemMailTemplate.objects.get(pk=110000)

        content_context = Context({
            "account": account
        })
        content_template = Template(mail_template.content)
        content = content_template.render(content_context)

        return dict(
            subject=mail_template.subject,
            title=mail_template.title,
            description=mail_template.description,
            content=content,
            comments=mail_template.comments
        )
