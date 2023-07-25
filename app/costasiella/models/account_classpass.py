from django.db import models
from django.db.models import Q
from django.utils import timezone

from .account import Account
from .organization_classpass import OrganizationClasspass
from .finance_payment_method import FinancePaymentMethod


class AccountClasspass(models.Model):
    # add additional fields in here
    # instructor and employee will use OneToOne fields. An account can optionally be a instructor or employee.
    # Editable parameter docs
    # https://docs.djangoproject.com/en/2.2/ref/models/fields/#editable

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="classpasses")
    organization_classpass = models.ForeignKey(OrganizationClasspass, on_delete=models.CASCADE)
    date_start = models.DateField()
    date_end = models.DateField(null=True)
    note = models.TextField(default="")
    classes_remaining = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.organization_classpass.name + ' [' + str(self.date_start) + ']'

    def update_classes_remaining(self):
        """ Calculate remaining classes """
        from .schedule_item_attendance import ScheduleItemAttendance
        
        if self.organization_classpass.unlimited:
            # No need to do anything for unlimited passes
            return
        else:
            total = self.organization_classpass.classes
            classes_taken = ScheduleItemAttendance.objects.exclude(
                booking_status="CANCELLED"
            ).filter(
                account_classpass=self
            ).count()
            self.classes_remaining = total - classes_taken
            self.save()

    def set_date_end(self):
        """
        Calculate and set enddate when adding a class pass
        return: datetime.date
        """
        def add_months(sourcedate, months):
            month = sourcedate.month - 1 + months
            year = int(sourcedate.year + month / 12)
            month = month % 12 + 1
            last_day_new = calendar.monthrange(year, month)[1]
            day = min(sourcedate.day, last_day_new)

            ret_val = datetime.date(year, month, day)

            last_day_source = calendar.monthrange(sourcedate.year,
                                                  sourcedate.month)[1]

            if sourcedate.day == last_day_source and last_day_source > last_day_new:
                return ret_val
            else:
                delta = datetime.timedelta(days=1)
                return ret_val - delta

        import datetime
        import calendar
        
        if self.organization_classpass.validity_unit == 'MONTHS':
            # check for and add months
            months = self.organization_classpass.validity
            if months:
                date_end = add_months(self.date_start, months)
        else:
            if self.organization_classpass.validity_unit == 'WEEKS':
                days = self.organization_classpass.validity * 7
            else:
                days = self.organization_classpass.validity

            delta_days = datetime.timedelta(days=days)
            date_end = (self.date_start + delta_days) - datetime.timedelta(days=1)

        self.date_end = date_end

        return date_end

    def is_expired(self):
        today = timezone.now().date()
        expired = False
        if today > self.date_end:
            expired = True

        return expired
        