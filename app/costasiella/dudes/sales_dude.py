from django.utils.translation import gettext as _


class SalesDude:
    def sell_classpass(self, account, organization_classpass, date_start, note="", create_invoice=True):
        """
        Sell classpass to account
        """
        from ..models.account_classpass import AccountClasspass

        account_classpass = AccountClasspass(
            account=account,
            organization_classpass=organization_classpass,
            date_start=date_start, 
            note=note
        )

        # set date end & save
        account_classpass.set_date_end()
        account_classpass.update_classes_remaining()
        account_classpass.save()

        print('creating invoice...')

        finance_invoice_item = None
        if create_invoice:
            print('still alive')
            finance_invoice_item = self._sell_classpass_create_invoice(account_classpass)

        return {
            "account_classpass": account_classpass,
            "finance_invoice_item": finance_invoice_item
        }

    @staticmethod
    def _sell_classpass_create_invoice(account_classpass):
        """
        Create an invoice for sold class pass
        """
        from ..models.finance_invoice_group_default import FinanceInvoiceGroupDefault
        from ..models.finance_invoice import FinanceInvoice

        finance_invoice_group_default = FinanceInvoiceGroupDefault.objects.filter(item_type="CLASSPASSES").first()
        finance_invoice_group = finance_invoice_group_default.finance_invoice_group
        print("invoice group")
        print(finance_invoice_group)

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
                          create_invoice=True):
        """
        Sell subscription to account
        """
        from ..models.account_subscription import AccountSubscription

        account_subscription = AccountSubscription(
            account=account,
            organization_subscription=organization_subscription,
            date_start=date_start,
            finance_payment_method=finance_payment_method,
            note=note
        )

        # set date end & save
        account_subscription.save()

        # Add credits
        account_subscription.create_credits_for_month(date_start.year, date_start.month)

        print('creating invoice...')

        finance_invoice_item = None
        if create_invoice:
            print('still alive')
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
        print("invoice group")
        print(finance_invoice_group)

        finance_invoice = FinanceInvoice(
            account=account_subscription.account,
            finance_invoice_group=finance_invoice_group,
            summary=_("Subscription %s" % account_subscription.id),
            status="SENT",
            terms=finance_invoice_group.terms,
            footer=finance_invoice_group.footer
        )

        # Save invoice
        finance_invoice.save()

        # Add invoice item
        year = account_subscription.date_start.year
        month = account_subscription.date_start.month
        finance_invoice_item = finance_invoice.item_add_subscription(account_subscription, year, month)

        return finance_invoice_item

    def sell_schedule_event_ticket(self,
                                   account,
                                   schedule_event_ticket,
                                   create_invoice=True):
        """
        Sell subscription to account
        """
        from ..models.account_schedule_event_ticket import AccountScheduleEventTicket
        from ..models.schedule_item_attendance import ScheduleItemAttendance

        account_schedule_event_ticket = AccountScheduleEventTicket(
            account=account,
            schedule_event_ticket=schedule_event_ticket
        )

        # set date end & save
        account_schedule_event_ticket.save()

        print('creating invoice...')
        finance_invoice_item = None
        if create_invoice:
            print('still alive')
            finance_invoice_item = self._sell_schedule_event_ticket_create_invoice(account_schedule_event_ticket)

        # Add account to schedule_item_attendance
        for schedule_item in schedule_event_ticket.schedule_items:
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

        return {
            "account_schedule_event_ticket": account_schedule_event_ticket,
            "finance_invoice_item": finance_invoice_item
        }

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
        print("invoice group")
        print(finance_invoice_group)

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
