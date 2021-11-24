import datetime
import calendar
from decimal import Decimal

from django.utils.translation import gettext as _
from django.db.models import Q, Sum


class InsightClassAttendanceDude:
    def get_attendance_count_class(self, schedule_item, date):
        """
        Return count of sold (new) subscriptions in a period
        """
        from ..models import ScheduleItemAttendance

        count = ScheduleItemAttendance.objects.filter(
            ~Q(status='CANCELLED'),
            schedule_item=schedule_item,
            date=date
        ).count()

        return count

    def get_attendance_count_recurring_class_year(self, schedule_item, year):
        """

        :param schedule_item:
        :param year:
        :return:
        """
        from collections import OrderedDict
        from .date_tools_dude import DateToolsDude

        date_tools_dude = DateToolsDude()

        iso_weekday = schedule_item.frequency_interval
        next_year = datetime.date(year + 1, 1, 1)
        first_weekday_in_year = date_tools_dude.get_first_day_of_week_of_year(year, iso_weekday)
        delta_one_week = datetime.timedelta(days=7)

        data = OrderedDict()
        date = first_weekday_in_year
        week = 0
        while date < next_year:
            if date < schedule_item.date_start:
                # Class hasn't started yet, no need to count, just return 0
                attendance = 0
            else:
                attendance = self.get_attendance_count_class(schedule_item, date)

            data[week] = attendance

            # Continue the loop
            date += delta_one_week

        return data


    #
    #
    # def get_subscriptions_sold_year_summary_count(self, year):
    #     """
    #     Return monthly counts of sold (new) subscriptions
    #     """
    #     data = []
    #
    #     print(year)
    #
    #     for i in range(1, 13):
    #         date_from = datetime.date(year, i, 1)
    #         last_day_month = calendar.monthrange(year, i)[1]
    #         date_until = datetime.date(year, i, last_day_month)
    #
    #         sold_in_month = self.get_subscriptions_sold_period_count(date_from, date_until)
    #         data.append(sold_in_month)
    #
    #     return data
    #
    #
    # def get_subscriptions_sold_period_data(self, date_from, date_until):
    #     """
    #     Return data list of sold (new) subscriptions in a period
    #     """
    #     from ..models import AccountSubscription
    #
    #     qs = AccountSubscription.objects.filter(
    #         date_start__gte = date_from,
    #         date_start__lte = date_until
    #     ).order_by("date_start")
    #
    #     return qs
    #
    #
    # def get_subscriptions_sold_year_data(self, year):
    #     """
    #     Get subscriptions sold (new) year data
    #     """
    #     from collections import OrderedDict
    #
    #     data = OrderedDict()
    #
    #     print(year)
    #
    #     for i in range(1, 13):
    #         date_from = datetime.date(year, i, 1)
    #         last_day_month = calendar.monthrange(year, i)[1]
    #         date_until = datetime.date(year, i, last_day_month)
    #
    #         subscriptions_sold_in_month = self.get_subscriptions_sold_period_data(date_from, date_until)
    #         data[i] = subscriptions_sold_in_month
    #
    #         # print(data)
    #
    #     return data
    #
    #
    # def get_subscriptions_active_period_count(self, date_from, date_until):
    #     """
    #     Return count of active subscriptions in a period
    #     """
    #     from ..models import AccountSubscription
    #
    #     count = AccountSubscription.objects.filter(
    #         (Q(date_end__gte = date_from) | Q(date_end__isnull=True)),
    #         date_start__lte = date_until,
    #     ).count()
    #
    #     print(count)
    #     return count
    #
    #
    # def get_subscriptions_active_year_summary_count(self, year):
    #     """
    #     Return monthly counts of active passes
    #     """
    #     data = []
    #
    #     print(year)
    #
    #     for i in range(1, 13):
    #         date_from = datetime.date(year, i, 1)
    #         last_day_month = calendar.monthrange(year, i)[1]
    #         date_until = datetime.date(year, i, last_day_month)
    #
    #         sold_in_month = self.get_subscriptions_active_period_count(date_from, date_until)
    #         data.append(sold_in_month)
    #
    #     return data
    #
    #
    # def get_subscriptions_active_period_data(self, date_from, date_until):
    #     """
    #     Return data list of active subscriptions in a period
    #     """
    #     from ..models import AccountSubscription
    #
    #     qs = AccountSubscription.objects.filter(
    #         (Q(date_end__gte = date_from) | Q(date_end__isnull=True)),
    #         date_start__lte = date_until,
    #     ).order_by("date_start")
    #
    #     return qs
    #
    #
    # def get_subscriptions_active_year_data(self, year):
    #     """
    #     Get subscriptions active year data
    #     """
    #     from collections import OrderedDict
    #
    #     data = OrderedDict()
    #
    #     print(year)
    #
    #     for i in range(1, 13):
    #         date_from = datetime.date(year, i, 1)
    #         last_day_month = calendar.monthrange(year, i)[1]
    #         date_until = datetime.date(year, i, last_day_month)
    #
    #         subscriptions_active_in_month = self.get_subscriptions_active_period_data(date_from, date_until)
    #         data[i] = subscriptions_active_in_month
    #
    #         # print(data)
    #
    #     return data
