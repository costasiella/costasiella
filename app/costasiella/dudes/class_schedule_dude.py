from django.utils.translation import gettext as _

class ClassScheduleDude:
    def schedule_item_takes_place_on_day(self, schedule_item, date):
        """
        :return: True if the schedule item takes place on given date
        False if not
        """
        # Check dates for specific classes
        if schedule_item.frequency_type == 'SPECIFIC':
            if schedule_item.date_start != date:
                # If dates don't match, the class isn't happening
                return False

        if schedule_item.frequency_type == 'WEEKLY':
            # Class doesn't happen when date is before start date
            if date < schedule_item.date_start:
                print('date start')
                return False

            if schedule_item.date_end:
                if date > schedule_item.date_end:
                    print('date end')
                    return False

            if date.isoweekday() != schedule_item.frequency_interval:
                # Wrong week day, the class isn't held on this day
                return False

        return True

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
