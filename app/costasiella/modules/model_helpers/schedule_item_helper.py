from django.db.models import Q

from ...models import OrganizationClasspassGroup, OrganizationSubscriptionGroup, \
                        OrganizationHolidayLocation, \
                        ScheduleEventTicket, ScheduleEventTicketScheduleItem, \
                        ScheduleItem, ScheduleItemWeeklyOTC, \
                        ScheduleItemOrganizationSubscriptionGroup, ScheduleItemOrganizationClasspassGroup

from ...dudes import ClassScheduleDude

"""
This helper file is added to allow function to add all subscription groups to a schedule item
ScheduleItem is already imported in the ScheduleItemOrganizationSubscriptionGroup model. 
Importing the SchedulItem model in ScheduleItemOrganizationSubscriptionGroup group generates an error.
"""


class ScheduleItemHelper:
    def add_all_subscription_groups(self, schedule_item_id):
        """
        Add all non-archived subscription groups to this schedule item
        """
        groups = OrganizationSubscriptionGroup.objects.all()

        for group in groups:
            schedule_item_subscription_group = ScheduleItemOrganizationSubscriptionGroup(
                schedule_item=ScheduleItem.objects.get(id=schedule_item_id),
                organization_subscription_group=group
            ).save()

    def add_all_classpass_groups(self, schedule_item_id):
        """
        Add all non-archived classpass groups to this schedule item
        """
        groups = OrganizationClasspassGroup.objects.all()
        for group in groups:
            schedule_item_classpass_group = ScheduleItemOrganizationClasspassGroup(
                schedule_item=ScheduleItem.objects.get(id=schedule_item_id),
                organization_classpass_group=group
            ).save()

    def add_schedule_item_to_all_event_tickets(self, schedule_item):
        """
        Add all tickets for an event to this schedule_item
        :param schedule_item: models.ScheduleItem object
        :return: None
        """
        schedule_event = schedule_item.schedule_event
        schedule_event_tickets = ScheduleEventTicket.objects.filter(
            schedule_event=schedule_event
        )

        for schedule_event_ticket in schedule_event_tickets:
            schedule_event_ticket_schedule_item = ScheduleEventTicketScheduleItem(
                schedule_event_ticket=schedule_event_ticket,
                schedule_item=schedule_item,
                included=schedule_event_ticket.full_event
            ).save()

    # def add_attendance_from_full_event_ticket(self, schedule_item):
    #     """
    #     Add all tickets for an event to this schedule_item
    #     :param schedule_item: models.ScheduleItem object
    #     :return: None
    #     """
    #     from ...models import AccountScheduleEventTicket, \
    #         FinanceInvoiceItem, \
    #         ScheduleItemAttendance
    #
    #     schedule_event = schedule_item.schedule_event
    #     full_event_ticket = schedule_event.get_full_schedule_event_ticket()
    #
    #     # Fetch customers who bought the ticket
    #     account_schedule_event_tickets = AccountScheduleEventTicket.objects.filter(
    #         schedule_event_ticket=full_event_ticket
    #     )
    #     for account_schedule_event_ticket in account_schedule_event_tickets:
    #         finance_invoice_item = FinanceInvoiceItem.objects.filter(
    #             account_schedule_event_ticket=account_schedule_event_ticket
    #         ).first()
    #
    #         booking_status = "BOOKED"
    #         if account_schedule_event_ticket.cancelled:
    #             booking_status = "CANCELLED"
    #
    #         schedule_item_attendance = ScheduleItemAttendance(
    #             account=account_schedule_event_ticket.account,
    #             schedule_item=schedule_item,
    #             account_schedule_event_ticket=account_schedule_event_ticket,
    #             finance_invoice_item=finance_invoice_item,
    #             attendance_type="SCHEDULE_EVENT_TICKET",
    #             booking_status=booking_status,
    #             date=schedule_item.date_start
    #         )
    #         schedule_item_attendance.save()
    #
    # def add_attendance_from_event_ticket(self, schedule_item, schedule_event_ticket):
    #     """
    #     Add all tickets for an event to this schedule_item
    #     :param schedule_item: models.ScheduleItem object
    #     :param account_schedule_event_ticket: models.AccountScheduleEventTicket object
    #     :return: None
    #     """
    #     from ...models import AccountScheduleEventTicket, \
    #         FinanceInvoiceItem, \
    #         ScheduleItemAttendance
    #
    #     # # Fetch & add full event ticket customers
    #     # self.add_attendance_from_full_event_ticket(schedule_item)
    #
    #     # Fetch & add customers who bought the ticket
    #     account_schedule_event_tickets = AccountScheduleEventTicket.objects.filter(
    #         schedule_event_ticket=schedule_event_ticket
    #     )
    #
    #     for account_schedule_event_ticket in account_schedule_event_tickets:
    #         finance_invoice_item = FinanceInvoiceItem.objects.filter(
    #             account_schedule_event_ticket=account_schedule_event_ticket
    #         ).first()
    #
    #         booking_status = "BOOKED"
    #         if account_schedule_event_ticket.cancelled:
    #             booking_status = "CANCELLED"
    #
    #         schedule_item_attendance, created = ScheduleItemAttendance.objects.filter(
    #             schedule_item=schedule_item,
    #             account_schedule_event_ticket=account_schedule_event_ticket
    #         ).get_or_create(
    #             account=account_schedule_event_ticket.account,
    #             schedule_item=schedule_item,
    #             account_schedule_event_ticket=account_schedule_event_ticket,
    #             finance_invoice_item=finance_invoice_item,
    #             attendance_type="SCHEDULE_EVENT_TICKET",
    #             booking_status=booking_status,
    #             date=schedule_item.date_start
    #         )

    def create_attendance_records_for_event_schedule_items(self, schedule_event):
        """
        Ensure schedule_item_attendance records for event ticket schedule events exist

        This function is safe, it won't overwrite existing records though the use of get_or_create.
        It can be executed where required
        :param schedule_event: models.ScheduleEvent object
        :return: None
        """
        # Find tickets for this event
        from ...models import AccountScheduleEventTicket, \
            FinanceInvoiceItem, \
            ScheduleEventTicket, ScheduleEventTicketScheduleItem, ScheduleItemAttendance

        schedule_event_tickets = ScheduleEventTicket.objects.filter(schedule_event=schedule_event)
        for schedule_event_ticket in schedule_event_tickets:
            # Fetch included items
            schedule_event_ticket_schedule_items = ScheduleEventTicketScheduleItem.objects.filter(
                schedule_event_ticket=schedule_event_ticket,
                included=True
            )
            # Fetch customers who bought the ticket
            account_schedule_event_tickets = AccountScheduleEventTicket.objects.filter(
                schedule_event_ticket=schedule_event_ticket
            )
            # For each ticket, check that there is an attendance record for customers that bought it.
            for schedule_event_ticket_schedule_item in schedule_event_ticket_schedule_items:
                schedule_item = schedule_event_ticket_schedule_item.schedule_item
                for account_schedule_event_ticket in account_schedule_event_tickets:
                    finance_invoice_item = FinanceInvoiceItem.objects.filter(
                        account_schedule_event_ticket=account_schedule_event_ticket
                    ).first()

                    booking_status = "BOOKED"
                    if account_schedule_event_ticket.cancelled:
                        booking_status = "CANCELLED"

                    schedule_item_attendance, created = ScheduleItemAttendance.objects.filter(
                        schedule_item=schedule_item,
                        account_schedule_event_ticket=account_schedule_event_ticket
                    ).get_or_create(
                        account=account_schedule_event_ticket.account,
                        schedule_item=schedule_item,
                        account_schedule_event_ticket=account_schedule_event_ticket,
                        finance_invoice_item=finance_invoice_item,
                        attendance_type="SCHEDULE_EVENT_TICKET",
                        booking_status=booking_status,
                        date=schedule_item.date_start
                    )

    def remove_attendance_from_event_ticket(self, schedule_item, schedule_event_ticket):
        """
        Add all tickets for an event to this schedule_item
        :param schedule_item: models.ScheduleItem object
        :param schedule_event_ticket: models.ScheduleEventTicket object
        :return: None
        """
        from ...models import ScheduleItemAttendance

        ScheduleItemAttendance.objects.filter(
            schedule_item=schedule_item,
            account_schedule_event_ticket__schedule_event_ticket=schedule_event_ticket
        ).delete()

    def schedule_item_with_otc_and_holiday_data(self, schedule_item, date):
        """
        Overwrite schedule_item object data with weekly otc data
        :param schedule_item: models.ScheduleItem object
        :param date: datetime.date
        :return:
        """
        # Check if there's a holiday
        class_schedule_dude = ClassScheduleDude()
        holiday_location = class_schedule_dude.schedule_item_is_within_holiday_on_day(schedule_item, date)

        if holiday_location:
            schedule_item.organization_holiday_id = holiday_location.organization_holiday.id
            schedule_item.organization_holiday_name = holiday_location.organization_holiday.name

        # No further processing required
        if schedule_item.schedule_item_type == 'SPECIFIC':
            return schedule_item

        # Check One Time Change (OTC) data
        schedule_item_weekly_otc_qs = ScheduleItemWeeklyOTC.objects.filter(
            schedule_item=schedule_item,
            date=date
        )

        schedule_item_weekly_otc = None
        if schedule_item_weekly_otc_qs.exists():
            schedule_item_weekly_otc = schedule_item_weekly_otc_qs.first()

            # Change schedule item in memory before returning, but DON'T save it!
            if schedule_item_weekly_otc.account:
                schedule_item.account = schedule_item_weekly_otc.account
                schedule_item.role = schedule_item_weekly_otc.role
            if schedule_item_weekly_otc.account_2:
                schedule_item.account = schedule_item_weekly_otc.account_2
                schedule_item.role = schedule_item_weekly_otc.role_2
            if schedule_item_weekly_otc.organization_location_room:
                schedule_item.organization_location_room = schedule_item_weekly_otc.organization_location_room
            if schedule_item_weekly_otc.organization_classtype:
                schedule_item.organization_classtype = schedule_item_weekly_otc.organization_classtype
            if schedule_item_weekly_otc.organization_level:
                schedule_item.organization_level = schedule_item_weekly_otc.organization_level
            if schedule_item_weekly_otc.time_start:
                schedule_item.time_start = schedule_item_weekly_otc.time_start
            if schedule_item_weekly_otc.time_end:
                schedule_item.time_end = schedule_item_weekly_otc.time_end
            if schedule_item_weekly_otc.info_mail_enabled:
                schedule_item.info_mail_enabled = schedule_item_weekly_otc.info_mail_enabled
            if schedule_item_weekly_otc.info_mail_content:
                schedule_item.info_mail_content = schedule_item_weekly_otc.info_mail_content
            if schedule_item_weekly_otc.status:
                schedule_item.status = schedule_item_weekly_otc.status
            if schedule_item_weekly_otc.description:
                schedule_item.description = schedule_item_weekly_otc.description
            if schedule_item_weekly_otc.spaces is not None:
                schedule_item.spaces = schedule_item_weekly_otc.spaces
            if schedule_item_weekly_otc.walk_in_spaces is not None:
                schedule_item.walk_in_spaces = schedule_item_weekly_otc.walk_in_spaces

        return schedule_item
