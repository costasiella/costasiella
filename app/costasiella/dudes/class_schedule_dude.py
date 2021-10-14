from django.utils.translation import gettext as _
from django.db.models import Q


class ClassScheduleDude:
    def schedule_item_takes_place_on_day(self, schedule_item, date):
        """
        :return: True if the schedule item takes place on given date
        False if not
        """
        takes_place = True

        # Check dates for specific classes
        valid_date = self.schedule_item_is_valid_date(schedule_item, date)
        if not valid_date:
            takes_place = False

        # check if cancelled
        is_cancelled = self.schedule_item_is_cancelled_on_day(schedule_item, date)
        if is_cancelled:
            takes_place = False

        # Check for holiday
        within_holiday = self.schedule_item_is_within_holiday_on_day(schedule_item, date)
        if within_holiday:
            takes_place = False

        return takes_place

    def schedule_item_is_valid_date(self, schedule_item, date):
        """
        Check if date is a correct day for the given schedule item
        :param schedule_item:
        :param date:
        :return:
        """
        valid_date = True
        # Check dates for specific classes
        if schedule_item.frequency_type == 'SPECIFIC':
            if schedule_item.date_start != date:
                # If dates don't match, the class isn't happening
                valid_date = False

        if schedule_item.frequency_type == 'WEEKLY':
            # Class doesn't happen when date is before start date
            if date < schedule_item.date_start:
                valid_date = False

            if schedule_item.date_end:
                if date > schedule_item.date_end:
                    valid_date = False

            if date.isoweekday() != schedule_item.frequency_interval:
                # Wrong week day, the class isn't held on this day
                valid_date = False

        return valid_date


    def schedule_item_is_cancelled_on_day(self, schedule_item, date):
        """

        :param schedule_item:
        :param date:
        :return:
        """
        from ..models import ScheduleItemWeeklyOTC

        schedule_item_weekly_otc = None

        qs = ScheduleItemWeeklyOTC.objects.filter(
            schedule_item=schedule_item,
            date=date,
            status='CANCELLED'
        )
        if qs.exists:
            schedule_item_weekly_otc = qs.first()

        return schedule_item_weekly_otc

    def schedule_item_is_within_holiday_on_day(self, schedule_item, date):
        """
        Check if the schedule item on given date falls within a holiday
        :param schedule_item: schedule_item object
        :param date: datetime.date
        :return:
        """
        from ..models import OrganizationHolidayLocation
        # Check if there's a holiday
        organization_location = schedule_item.organization_location_room.organization_location
        qs_holiday_locations = OrganizationHolidayLocation.objects.filter(
            (Q(organization_holiday__date_start__lte = date) & Q(organization_holiday__date_end__gte = date)) &
             Q(organization_location = organization_location)
        )

        holiday_location = None
        if qs_holiday_locations.exists():
            holiday_location = qs_holiday_locations.first()

        return holiday_location

    def schedule_class_with_otc_data(self, schedule_item, date):
        """
        Fetch a schedule_item and check for otc data. If found, add it to the item.
        :param schedule_item:
        :param date:
        :return:
        """
        from ..models import ScheduleItem, ScheduleItemWeeklyOTC

        schedule_item_weekly_otc = None
        qs = ScheduleItemWeeklyOTC.objects.filter(
            schedule_item=schedule_item,
            date=date
        )
        if qs.exists:
            schedule_item_weekly_otc = qs.first()

        if schedule_item_weekly_otc:
            if schedule_item_weekly_otc.time_start:
                schedule_item.time_start = schedule_item_weekly_otc.time_start

            if schedule_item_weekly_otc.time_end:
                schedule_item.time_end = schedule_item_weekly_otc.time_end

            if schedule_item_weekly_otc.info_mail_content:
                schedule_item.info_mail_content = schedule_item_weekly_otc.info_mail_content

            if schedule_item_weekly_otc.organization_classtype:
                schedule_item.organization_classtype = schedule_item_weekly_otc.organization_classtype

            if schedule_item_weekly_otc.organization_location_room:
                schedule_item.organization_location_room = schedule_item_weekly_otc.organization_location_room

            if schedule_item_weekly_otc.organization_level:
                schedule_item.organization_level = schedule_item_weekly_otc.organization_level

        return schedule_item
