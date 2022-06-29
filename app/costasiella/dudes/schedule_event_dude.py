from django.utils.translation import gettext as _


class ScheduleEventDude:
    def duplicate(self, schedule_event):
        from ..models import ScheduleEvent, \
            ScheduleEventEarlybird, \
            ScheduleEventMedia, \
            ScheduleEventTicket, \
            ScheduleItem

        from ..modules.model_helpers.schedule_event_ticket_schedule_item_helper import \
            ScheduleEventTicketScheduleItemHelper
        from ..modules.model_helpers.schedule_item_helper import ScheduleItemHelper

        item_helper = ScheduleItemHelper()
        ticket_helper = ScheduleEventTicketScheduleItemHelper()

        # Duplicate event, don't put in the shop or publish to website by default
        new_schedule_event = ScheduleEvent(
            archived=schedule_event.archived,
            display_public=False,
            display_shop=False,
            auto_send_info_mail=schedule_event.auto_send_info_mail,
            organization_location=schedule_event.organization_location,
            name=schedule_event.name + " " + _("(Duplicated)"),
            tagline=schedule_event.tagline,
            preview=schedule_event.preview,
            description=schedule_event.description,
            organization_level=schedule_event.organization_level,
            instructor=schedule_event.instructor,
            instructor_2=schedule_event.instructor_2,
            date_start=schedule_event.date_start,
            date_end=schedule_event.date_end,
            time_start=schedule_event.time_start,
            time_end=schedule_event.time_end,
            info_mail_content=schedule_event.info_mail_content
        )

        new_schedule_event.save()

        # Duplicate schedule_items linked to schedule_event
        schedule_items_to_be_duplicated = ScheduleItem.objects.filter(
            schedule_event=schedule_event
        )

        for schedule_item in schedule_items_to_be_duplicated:
            new_schedule_item = ScheduleItem(
                schedule_event=new_schedule_event,
                schedule_item_type=schedule_item.schedule_item_type,
                frequency_type=schedule_item.frequency_type,
                frequency_interval=schedule_item.frequency_interval,
                organization_location_room=schedule_item.organization_location_room,
                organization_classtype=schedule_item.organization_classtype,
                organization_level=schedule_item.organization_level,
                organization_shift=schedule_item.organization_shift,
                name=schedule_item.name,
                spaces=schedule_item.spaces,
                walk_in_spaces=schedule_item.walk_in_spaces,
                date_start=schedule_item.date_start,
                date_end=schedule_item.date_end,
                time_start=schedule_item.time_start,
                time_end=schedule_item.time_end,
                display_public=schedule_item.display_public,
                info_mail_content=schedule_item.info_mail_content,
                account=schedule_item.account,
                account_2=schedule_item.account_2
            )
            new_schedule_item.save()

            # Add Schedule item to all tickets
            item_helper.add_schedule_item_to_all_event_tickets(new_schedule_item)
            # Add attendance records (eg. full event ticket customers should always be added).
            item_helper.create_attendance_records_for_event_schedule_items(new_schedule_item.schedule_event)

            # update event dates & times
            new_schedule_item.schedule_event.update_dates_and_times()

        # Duplicate tickets
        tickets_to_be_duplicated = ScheduleEventTicket.objects.filter(
            schedule_event=schedule_event,
        )

        for ticket in tickets_to_be_duplicated:
            new_schedule_event_ticket = ScheduleEventTicket(
                schedule_event=new_schedule_event,
                full_event=ticket.full_event,
                deletable=ticket.deletable,
                display_public=ticket.display_public,
                name=ticket.name,
                description=ticket.description,
                price=ticket.price,
                finance_tax_rate=ticket.finance_tax_rate,
                finance_glaccount=ticket.finance_glaccount,
                finance_costcenter=ticket.finance_costcenter
            )
            new_schedule_event_ticket.save()

            # Add schedule items to ticket
            ticket_helper.add_schedule_items_to_ticket(new_schedule_event_ticket)

        # Duplicate media
        media_to_be_duplicated = ScheduleEventMedia.objects.filter(schedule_event=schedule_event)

        for media in media_to_be_duplicated:
            new_schedule_event_media = ScheduleEventMedia(
                schedule_event=new_schedule_event,
                sort_order=media.sort_order,
                description=media.description,
                image=media.image
            )
            new_schedule_event_media.save()

        # Duplicate earlybird discounts
        earlybirds_to_be_duplicated = ScheduleEventEarlybird.objects.filter(schedule_event=schedule_event)

        for earlybird in earlybirds_to_be_duplicated:
            new_schedule_event_earlybird = ScheduleEventEarlybird(
                schedule_event=new_schedule_event,
                date_start=earlybird.date_start,
                date_end=earlybird.date_end,
                discount_percentage=earlybird.discount_percentage
            )
            new_schedule_event_earlybird.save()

        return new_schedule_event
