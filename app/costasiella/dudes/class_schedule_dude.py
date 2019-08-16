from django.utils.translation import gettext as _

from ..models import ScheduleItem


class ClassScheduleDude():
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
                if date > date_end:
                    print('date end')
                    return False

            if date.isoweekday() != schedule_item.frequency_interval:
                # Wrong week day, the class isn't held on this day
                return False

        return True
