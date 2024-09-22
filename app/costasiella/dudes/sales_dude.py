from django.utils.translation import gettext as _
from django.utils import timezone

import datetime

from .date_tools_dude import DateToolsDude

class SalesDude:
    def sell_membership(self,
                        account,
                        organization_membership,
                        finance_payment_method,
                        date_start,
                        note="",
                        create_invoice=True):
        """
        Sell classpass to account
        """
        from ..models.account_membership import AccountMembership

        account_membership = AccountMembership(
            account=account,
            organization_membership=organization_membership,
            finance_payment_method=finance_payment_method,
            date_start=date_start,
            note=note
        )

        # set date end & save
        account_membership.set_date_end()
        account_membership.save()

        finance_invoice_item = None
        if create_invoice:
            finance_invoice_item = self._sell_membership_create_invoice(account_membership)

        return {
            "account_membership": account_membership,
            "finance_invoice_item": finance_invoice_item
        }

    @staticmethod
    def _sell_membership_create_invoice(account_membership):
        """
        Create an invoice for sold membership
        """
        from ..models.finance_invoice_group_default import FinanceInvoiceGroupDefault
        from ..models.finance_invoice import FinanceInvoice

        finance_invoice_group_default = FinanceInvoiceGroupDefault.objects.filter(item_type="MEMBERSHIPS").first()
        finance_invoice_group = finance_invoice_group_default.finance_invoice_group
        finance_invoice = FinanceInvoice(
            account=account_membership.account,
            finance_invoice_group=finance_invoice_group,
            summary=account_membership.organization_membership.name,
            status="SENT",
            terms=finance_invoice_group.terms,
            footer=finance_invoice_group.footer
        )

        # Save invoice
        finance_invoice.save()

        # Add invoice item
        finance_invoice_item = finance_invoice.item_add_membership(account_membership)

        return finance_invoice_item

    def sell_classpass(self, account, organization_classpass, date_start, note="", create_invoice=True):
        """
        Sell classpass to account
        """
        from ..models.account_classpass import AccountClasspass

        # Check if this is a trial pass and if so, if the customer isn't over the trial limit
        self._sell_classpass_account_is_over_trial_pass_limit(account, organization_classpass)

        account_classpass = AccountClasspass(
            account=account,
            organization_classpass=organization_classpass,
            date_start=date_start,
            note=note
        )

        # set date end & save
        account_classpass.set_date_end()
        account_classpass.save() # Save before running classes remaining update; otherwise it doesn't haven an ID yet.
        account_classpass.update_classes_remaining()
        account_classpass.save()

        finance_invoice_item = None
        if create_invoice:
            finance_invoice_item = self._sell_classpass_create_invoice(account_classpass)

        return {
            "account_classpass": account_classpass,
            "finance_invoice_item": finance_invoice_item
        }

    @staticmethod
    def _sell_classpass_account_is_over_trial_pass_limit(account, organization_classpass):
        """
        Check if this account is allowed to purchase another trial card.
        """
        from ..models import AccountClasspass

        if not organization_classpass.trial_pass:
            # Nothing to do
            return

        if account.has_reached_trial_limit():
            raise Exception(_("Unable to sell classpass: Maximum number of trial passes reached for this account"))

    @staticmethod
    def _sell_classpass_create_invoice(account_classpass):
        """
        Create an invoice for sold class pass
        """
        from ..models.finance_invoice_group_default import FinanceInvoiceGroupDefault
        from ..models.finance_invoice import FinanceInvoice

        finance_invoice_group_default = FinanceInvoiceGroupDefault.objects.filter(item_type="CLASSPASSES").first()
        finance_invoice_group = finance_invoice_group_default.finance_invoice_group
        finance_invoice = FinanceInvoice(
            account=account_classpass.account,
            finance_invoice_group=finance_invoice_group,
            summary=_("Class pass %s" % account_classpass.id),
            status="SENT",
            terms=finance_invoice_group.terms,
            footer=finance_invoice_group.footer
        )

        # Save invoice
        finance_invoice.save()

        # Add invoice item
        finance_invoice_item = finance_invoice.item_add_classpass(account_classpass)

        return finance_invoice_item

    def sell_subscription(self,
                          account,
                          organization_subscription,
                          date_start,
                          finance_payment_method,
                          note="",
                          date_end=None,
                          create_invoice=True,
                          next_month_credits_after_day=15):
        """
        Sell subscription to account
        """
        from ..models.account_subscription import AccountSubscription

        account_subscription = AccountSubscription(
            account=account,
            organization_subscription=organization_subscription,
            date_start=date_start,
            date_end=date_end,
            finance_payment_method=finance_payment_method,
            note=note
        )

        # Set date end & save
        account_subscription.save()

        # Add credits
        account_subscription.create_credits_for_month(date_start.year, date_start.month)

        # Check if it's past the 15th of the month and if so, add credits for the next month as well
        now = timezone.now()
        day_of_month = now.date().day

        if day_of_month >= next_month_credits_after_day:
            # Get next month
            date_tools_dude = DateToolsDude()

            first_day_this_month = datetime.date(date_start.year, date_start.month, 1)
            first_day_next_month = date_tools_dude.get_first_day_of_next_month_from_date(first_day_this_month)

            account_subscription.create_credits_for_month(first_day_next_month.year, first_day_next_month.month)

        # Create invoice
        finance_invoice_item = None
        if create_invoice:
            finance_invoice_item = self._sell_subscription_create_invoice(account_subscription)

        return {
            "account_subscription": account_subscription,
            "finance_invoice_item": finance_invoice_item
        }

    @staticmethod
    def _sell_subscription_create_invoice(account_subscription):
        """
        Create an invoice for sold subscription.
        This function should only be used for the 1st invoice for a subscription
        """
        from ..models.finance_invoice_group_default import FinanceInvoiceGroupDefault
        from ..models.finance_invoice import FinanceInvoice

        finance_invoice_group_default = FinanceInvoiceGroupDefault.objects.filter(item_type="SUBSCRIPTIONS").first()
        finance_invoice_group = finance_invoice_group_default.finance_invoice_group

        finance_invoice = FinanceInvoice(
            account=account_subscription.account,
            finance_invoice_group=finance_invoice_group,
            summary=_("Subscription %s" % account_subscription.id),
            status="SENT",
            terms=finance_invoice_group.terms,
            footer=finance_invoice_group.footer
        )

        # Use the payment method set on the account subscription, if set.
        if account_subscription.finance_payment_method:
            finance_invoice.finance_payment_method = account_subscription.finance_payment_method

        # Save invoice
        finance_invoice.save()

        # Add invoice item
        year = account_subscription.date_start.year
        month = account_subscription.date_start.month
        finance_invoice_item = finance_invoice.item_add_subscription(account_subscription, year, month)

        return finance_invoice_item

    def _sell_schedule_event_ticket_send_info_mail(self, account, account_schedule_event_ticket):
        """
        Send info mail to customer, if configured.
        :param account: models.Account object
        :param account_schedule_event_ticket: models.AccountScheduleEventTicket object
        :return:
        """
        from ..dudes.mail_dude import MailDude

        mail_dude = MailDude(account=account,
                             email_template="event_info_mail",
                             account_schedule_event_ticket=account_schedule_event_ticket)
        success = mail_dude.send()

        if success:
            account_schedule_event_ticket.info_mail_sent = True
            account_schedule_event_ticket.save()


    def sell_schedule_event_ticket(self,
                                   account,
                                   schedule_event_ticket,
                                   create_invoice=True):
        """
        Sell subscription to account
        """
        from ..models.account_schedule_event_ticket import AccountScheduleEventTicket

        schedule_event = schedule_event_ticket.schedule_event
        account_schedule_event_ticket = AccountScheduleEventTicket(
            account=account,
            schedule_event_ticket=schedule_event_ticket
        )

        # set date end & save
        account_schedule_event_ticket.save()

        # Send info mail... if auto send mail is enabled
        if schedule_event.auto_send_info_mail:
            self._sell_schedule_event_ticket_send_info_mail(
                account=account,
                account_schedule_event_ticket=account_schedule_event_ticket
            )

        finance_invoice_item = None
        if create_invoice:
            finance_invoice_item = self._sell_schedule_event_ticket_create_invoice(account_schedule_event_ticket)

        # Add account to schedule_item_attendance
        self._sell_schedule_event_ticket_add_attendance(
            account_schedule_event_ticket=account_schedule_event_ticket,
            finance_invoice_item=finance_invoice_item
        )

        return {
            "account_schedule_event_ticket": account_schedule_event_ticket,
            "finance_invoice_item": finance_invoice_item
        }

    @staticmethod
    def _sell_schedule_event_ticket_add_attendance(account_schedule_event_ticket, finance_invoice_item):
        """
        Add an schedule_item_attendance record with status BOOKED for each schedule item linked to this ticket
        :return: None
        """
        from ..models.schedule_item_attendance import ScheduleItemAttendance
        from ..models.schedule_event_ticket_schedule_item import ScheduleEventTicketScheduleItem

        account = account_schedule_event_ticket.account
        schedule_event_ticket = account_schedule_event_ticket.schedule_event_ticket

        for schedule_event_ticket_schedule_item in ScheduleEventTicketScheduleItem.objects.filter(
            schedule_event_ticket=schedule_event_ticket,
            included=True
        ):
            schedule_item = schedule_event_ticket_schedule_item.schedule_item
            schedule_item_attendance = ScheduleItemAttendance(
                account=account,
                schedule_item=schedule_item,
                account_schedule_event_ticket=account_schedule_event_ticket,
                finance_invoice_item=finance_invoice_item,
                attendance_type="SCHEDULE_EVENT_TICKET",
                booking_status="BOOKED",
                date=schedule_item.date_start
            )
            schedule_item_attendance.save()

    @staticmethod
    def _sell_schedule_event_ticket_create_invoice(account_schedule_event_ticket):
        """
        Create an invoice for sold subscription.
        This function should only be used for the 1st invoice for a subscription
        """
        from ..models.finance_invoice_group_default import FinanceInvoiceGroupDefault
        from ..models.finance_invoice import FinanceInvoice

        finance_invoice_group_default = FinanceInvoiceGroupDefault.objects.filter(item_type="EVENT_TICKETS").first()
        finance_invoice_group = finance_invoice_group_default.finance_invoice_group
        finance_invoice = FinanceInvoice(
            account=account_schedule_event_ticket.account,
            finance_invoice_group=finance_invoice_group,
            summary=_("Event ticket: %s - %s" % (
                account_schedule_event_ticket.schedule_event_ticket.schedule_event.name,
                account_schedule_event_ticket.schedule_event_ticket.name
            )),
            status="SENT",
            terms=finance_invoice_group.terms,
            footer=finance_invoice_group.footer
        )

        # Save invoice
        finance_invoice.save()

        # Add invoice item
        finance_invoice_item = finance_invoice.item_add_schedule_event_ticket(account_schedule_event_ticket)

        return finance_invoice_item

    def sell_product(self, account, organization_product, quantity, create_invoice=True):
        """
        Sell product to account
        """
        from ..models.account_product import AccountProduct

        account_product = AccountProduct(
            account=account,
            organization_product=organization_product,
            quantity=quantity,
        )

        account_product.save()

        finance_invoice_item = None
        if create_invoice:
            finance_invoice_item = self._sell_product_create_invoice(account_product)

        return {
            "account_product": account_product,
            "finance_invoice_item": finance_invoice_item
        }

    @staticmethod
    def _sell_product_create_invoice(account_product):
        """
        Create an invoice for sold product
        """
        from ..models.finance_invoice_group_default import FinanceInvoiceGroupDefault
        from ..models.finance_invoice import FinanceInvoice

        finance_invoice_group_default = FinanceInvoiceGroupDefault.objects.filter(item_type="PRODUCTS").first()
        finance_invoice_group = finance_invoice_group_default.finance_invoice_group
        finance_invoice = FinanceInvoice(
            account=account_product.account,
            finance_invoice_group=finance_invoice_group,
            summary=account_product.organization_product.name,
            status="SENT",
            terms=finance_invoice_group.terms,
            footer=finance_invoice_group.footer
        )

        # Save invoice
        finance_invoice.save()

        # Add invoice item
        finance_invoice_item = finance_invoice.item_add_product(account_product)

        return finance_invoice_item
