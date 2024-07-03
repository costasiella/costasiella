import datetime

from django.utils.translation import gettext as _
from django.utils import timezone
from django.db.models import Q


from ..modules.cs_errors import \
    CSClassFullyBookedError, \
    CSClassDoesNotTakePlaceOnDateError, \
    CSClassBookingSubscriptionAlreadyBookedError, \
    CSClassBookingSubscriptionBlockedError, \
    CSClassBookingSubscriptionPausedError, \
    CSClassBookingSubscriptionNoCreditsError, \
    CSSubscriptionNotValidOnDateError


class ClassCheckinDude:
    def send_info_mail(self, account, schedule_item, date):
        """
        Send info mail to customer, if configured.
        :param account: models.Account object
        :param schedule_item: models.ScheduleItem object
        :param date: datetime.date object
        :return:
        """
        from ..modules.model_helpers.schedule_item_helper import ScheduleItemHelper
        from ..dudes.mail_dude import MailDude

        # Use the helper to make sure we're also checking one time change (otc) data
        sih = ScheduleItemHelper()
        schedule_item = sih.schedule_item_with_otc_and_holiday_data(schedule_item, date)

        if schedule_item.info_mail_enabled:
            mail_dude = MailDude(account=account,
                                 email_template="class_info_mail",
                                 schedule_item=schedule_item,
                                 date=date)
            mail_dude.send()

    def class_check_checkedin(self, account, schedule_item, date):
        """
        :param account: models.Account object
        :param schedule_item: models.ScheduleItem object
        :param date: datetime.date object
        :return: Boolean; true if the account is already checked-in for the class, false otherwise
        """
        qs = self.account_is_attending_class(account, schedule_item, date)

        return qs.exists()

    def account_is_attending_class(self, account, schedule_item, date):
        """
        :return: schedule_item_attendance object if found, so we can check for reviews
        """
        from ..models import ScheduleItemAttendance
        schedule_item_attendance = ScheduleItemAttendance.objects.filter(
            Q(account=account),
            Q(schedule_item=schedule_item),
            Q(date=date),
            # ~Q(booking_status="CANCELLED")
        )
        
        return schedule_item_attendance

    def check_class_is_full(self, schedule_item, date):
        from ..models import ScheduleItemAttendance
        # from ..schema.schedule_class import calculate_available_spaces_online

        is_full = False
        spaces_total = schedule_item.spaces
        qs = ScheduleItemAttendance.objects.filter(
            Q(schedule_item=schedule_item),
            Q(date=date),
            ~Q(booking_status="CANCELLED")
        )
        spaces_taken = qs.count()
        # We could look at online spaces only here, but it's also nice to allow as many people as possible to
        # uncancel their cancellations.
        if spaces_total - spaces_taken < 1:
            is_full = True

        return is_full


    def sell_classpass_and_class_checkin(self, 
                                         account,
                                         organization_classpass,
                                         schedule_item,
                                         date,
                                         booking_status=False,
                                         online_booking="BOOKED"):
        """
        :return: ScheduleItemAttendance and AccountClasspass objects if successful
        Raise error when not successful
        """
        # Check if not already signed in
        qs = self.account_is_attending_class(account, schedule_item, date)
        if qs.exists():
            # Already signed in, check for review check-in
            schedule_item_attendance = qs.first()

            if not schedule_item_attendance == 'REVIEW':
                raise Exception(_('This account is already checked in to this class'))
            # else:
            #TODO: Write review check-ins code

        from .sales_dude import SalesDude
        sales_dude = SalesDude()
        sales_result = sales_dude.sell_classpass(
            account=account, 
            organization_classpass=organization_classpass, 
            date_start=date
        )
        account_classpass = sales_result['account_classpass']

        schedule_item_attendance = self.class_checkin_classpass(
            account=account,
            account_classpass=account_classpass,
            schedule_item=schedule_item,
            date=date,
            online_booking=online_booking,
            booking_status=booking_status,
        )

        return {
            "schedule_item_attendance": schedule_item_attendance,
            "account_classpass": account_classpass
        }

    def class_checkin_classpass(self, 
                                account,
                                account_classpass,
                                schedule_item,
                                date,
                                online_booking=False,
                                booking_status="BOOKED"):
        """
        :return: ScheduleItemAttendance object if successful, raise error if not.
        """
        from ..models import ScheduleItemAttendance

        # Check if not already signed in
        qs = self.account_is_attending_class(account, schedule_item, date)
        if qs.exists():
            # Already signed in, check for review check-in
            schedule_item_attendance = qs.first()

            if not schedule_item_attendance == 'REVIEW':
                raise Exception(_('This account is already checked in to this class'))
            # else:
            #TODO: Write review check-ins code

        # Verify classpass belongs to account
        if account_classpass.account != account:
            raise Exception(_("This classpass doesn't belong to this account"))

        # Check if classes left on pass
        classes_available = False
        if account_classpass.organization_classpass.unlimited:
            classes_available = True
        if account_classpass.classes_remaining:
            classes_available = True

        if not classes_available:
            raise Exception(_('No classes left on this pass.'))

        # Check pass valid on date
        if (date < account_classpass.date_start) or (date > account_classpass.date_end):
            raise Exception(_('This pass is not valid on this date.'))

        schedule_item_attendance = ScheduleItemAttendance(
            attendance_type="CLASSPASS",
            account=account,
            account_classpass=account_classpass,
            schedule_item=schedule_item,
            date=date,
            online_booking=online_booking,
            booking_status=booking_status
        )

        schedule_item_attendance.save()
        account_classpass.update_classes_remaining()
        account_classpass.save()

        self.send_info_mail(
            account=account,
            schedule_item=schedule_item,
            date=date,
        )

        return schedule_item_attendance

    # def attendance_sign_in_classcard(self, cuID, clsID, ccdID, date, online_booking=False, booking_status='booked'):
    #     """
    #         :param cuID: db.auth_user.id 
    #         :param clsID: db.classes.id
    #         :param ccdID: db.customers_classcards.id
    #         :param date: datetime.date
    #         :return: 
    #     """
    #     from .os_customer_classcard import CustomerClasscard

    #     db = current.db
    #     T = current.T

    #     ccd = CustomerClasscard(ccdID)
    #     classes_available = ccd.get_classes_available()

    #     status = 'fail'
    #     message = ''
    #     if classes_available or ccd.school_classcard.Unlimited:
    #         class_data = dict(
    #             auth_customer_id=cuID,
    #             CustomerMembership=self._attendance_sign_in_has_membership(cuID, date),
    #             classes_id=clsID,
    #             ClassDate=date,
    #             AttendanceType=3,  # 3 = classcard
    #             customers_classcards_id=ccdID,
    #             online_booking=online_booking,
    #             BookingStatus=booking_status
    #         )

    #         signed_in = self._attendance_sign_in_check_signed_in(clsID, cuID, date)
    #         if signed_in:
    #             if signed_in.AttendanceType == 5:
    #                 # Under review, so update
    #                 status = 'ok'
    #                 db(db.classes_attendance._id == signed_in.id).update(**class_data)
    #             else:
    #                 message = T("Already checked in for this class")
    #         else:
    #             status = 'ok'

    #             db.classes_attendance.insert(
    #                 **class_data
    #             )

    #             # update class count
    #             ccd.set_classes_taken()
    #     else:
    #         message = T("Unable to add, no classes left on card")
    #     return dict(status=status, message=message)
    # def classpass_class_permissions(self, account_classpass, public_only=True):

    def classpass_class_permissions(self, account_classpass):
        """
        :return: return list of class permissons
        """
        from ..models import OrganizationClasspassGroupClasspass, ScheduleItemOrganizationClasspassGroup
        organization_classpass = account_classpass.organization_classpass

        # Get groups for class pass
        group_ids = OrganizationClasspassGroupClasspass.objects.filter(
            organization_classpass=organization_classpass
        ).values_list('organization_classpass_group__id', flat=True)
        # group_ids = []
        # for group in qs_groups:
        #     group_ids.append(group.id)

        # Get permissions for groups
        qs_permissions = ScheduleItemOrganizationClasspassGroup.objects.filter(
            organization_classpass_group__in = group_ids
        )

        permissions = {}
        for schedule_item_organization_classpass_group in qs_permissions:
            schedule_item_id = schedule_item_organization_classpass_group.schedule_item_id

            if schedule_item_id not in permissions:
                permissions[schedule_item_id] = {}

            if schedule_item_organization_classpass_group.shop_book:
                permissions[schedule_item_id]['shop_book'] = True

            if schedule_item_organization_classpass_group.attend:
                permissions[schedule_item_id]['attend'] = True

        return permissions

    def classpass_attend_allowed(self, account_classpass):
        """
        Returns True is a class pass is allowed for a class,
        otherwise False
        """
        permissions = self.classpass_class_permissions(account_classpass)

        schedule_item_ids = []
        for schedule_item_id in permissions:
            try:
                if permissions[schedule_item_id]['attend']:
                    schedule_item_ids.append(schedule_item_id)
            except KeyError:
                pass

        return schedule_item_ids
    
    def classpass_attend_allowed_for_class(self, account_classpass, schedule_item):
        """
        :return: True if a classpass has the attend permission for a class
        """
        classes_allowed = self.classpass_attend_allowed(account_classpass)

        if schedule_item.id in classes_allowed:
            return True
        else:
            return False

    def classpass_shop_book_allowed(self, account_classpass):
        """
        Returns True is a class pass is allowed for a class,
        otherwise False
        """
        permissions = self.classpass_class_permissions(account_classpass)

        schedule_item_ids = []
        for schedule_item_id in permissions:
            try:
                if permissions[schedule_item_id]['shop_book']:
                    schedule_item_ids.append(schedule_item_id)
            except KeyError:
                pass

        return schedule_item_ids

    def classpass_shop_book_allowed_for_class(self, account_classpass, schedule_item):
        """
        :return: True if a classpass has the attend permission for a class
        """
        classes_allowed = self.classpass_shop_book_allowed(account_classpass)

        if schedule_item.id in classes_allowed:
            return True
        else:
            return False

    def class_checkin_subscription(self, 
                                   account,
                                   account_subscription,
                                   schedule_item,
                                   date,
                                   online_booking=False,
                                   booking_status="BOOKED"):
        """
        :return: ScheduleItemAttendance object if successful, raise error if not.
        """
        from .class_schedule_dude import ClassScheduleDude
        from ..models import ScheduleItemAttendance

        # Check if not already signed in
        qs = self.account_is_attending_class(account, schedule_item, date)
        if qs.exists():
            # Already signed in, check for review check-in
            schedule_item_attendance = qs.first()

            if not schedule_item_attendance == 'REVIEW':
                raise CSClassBookingSubscriptionAlreadyBookedError(
                    _('This account is already checked in to this class')
                )
            # else:
            #TODO: Write review check-ins code

        # Check for correct account
        if account_subscription.account != account:
            raise Exception(_("This subscription doesn't belong to this account"))

        # Check credits remaining if not unlimited
        if (account_subscription.get_usable_credits_total(date)) < 1 and \
                not account_subscription.organization_subscription.unlimited:
            raise CSClassBookingSubscriptionNoCreditsError(
                _(f"Insufficient credits available on {date} to book this class"))

        # Check blocked:
        if account_subscription.get_blocked_on_date(date):
            raise CSClassBookingSubscriptionBlockedError(_(f"This subscription is blocked on {date}"))

        # Check paused:
        if account_subscription.get_paused_on_date(date):
            raise CSClassBookingSubscriptionPausedError(_(f"This subscription is paused on {date}"))

        #TODO: Put the next two checks into a general function that can be used in all check-in functions

        # Check full
        if self.check_class_is_full(schedule_item, date):
            raise CSClassFullyBookedError(_(f"This class is fully booked on {date}"))

        # Check class takes place
        class_schedule_dude = ClassScheduleDude()
        if not class_schedule_dude.schedule_item_takes_place_on_day(schedule_item, date):
            raise CSClassDoesNotTakePlaceOnDateError(_(f"This class doesn't take place on {date}"))

        # Subscription valid on date
        if account_subscription.date_end:
            date_invalid_condition = (date < account_subscription.date_start) or (date > account_subscription.date_end)
        else:
            date_invalid_condition = (date < account_subscription.date_start)

        if date_invalid_condition:
            raise CSSubscriptionNotValidOnDateError(_('This subscription is not valid on this date.'))

        # Book class
        schedule_item_attendance = ScheduleItemAttendance(
            attendance_type="SUBSCRIPTION",
            account=account,
            account_subscription=account_subscription,
            schedule_item=schedule_item,
            date=date,
            online_booking=online_booking,
            booking_status=booking_status
        )
        schedule_item_attendance.save()

        # Take credit (Link oldest credit to attendance)
        self.class_checkin_subscription_take_credit(
            schedule_item_attendance=schedule_item_attendance
        )

        # Send info mail
        self.send_info_mail(
            account=account,
            schedule_item=schedule_item,
            date=date,
        )

        return schedule_item_attendance

    def class_checkin_subscription_take_credit(self, schedule_item_attendance):
        from ..models import AccountSubscriptionCredit

        account_subscription = schedule_item_attendance.account_subscription
        # Take credit (Link oldest credit to attendance)
        # Give a credit for unlimited subscriptions, so booking is always possible
        if account_subscription.organization_subscription.unlimited:
            account_subscription_credit = AccountSubscriptionCredit(
                account_subscription=account_subscription,
                expiration=timezone.now().date(),
                description=_("Unlimited")
            )
            account_subscription_credit.save()
        elif account_subscription.get_credits_total(schedule_item_attendance.date) < 1:
            # Give an advance credit if total credits < 0
            # This is ok, because above is a guard clause that checks for the hard limit (with advance credits included)
            today = timezone.now().date()
            validity_in_days = account_subscription.organization_subscription.credit_validity
            expiration = today + datetime.timedelta(days=validity_in_days)

            account_subscription_credit = AccountSubscriptionCredit(
                advance=True,
                account_subscription=account_subscription,
                expiration=expiration,
                description=_("Advance credit")
            )
            account_subscription_credit.save()
        else:
            # Regular flow, get next credit in line (first in, first out)
            account_subscription_credit = account_subscription.get_next_credit(
                schedule_item_attendance.date
            )

        account_subscription_credit.schedule_item_attendance = schedule_item_attendance
        account_subscription_credit.save()

    def subscription_class_permissions(self, account_subscription):
        """
        :return: return list of class permissons for this subscription
        """
        from ..models import OrganizationSubscriptionGroupSubscription, ScheduleItemOrganizationSubscriptionGroup

        organization_subscription = account_subscription.organization_subscription

        # Get groups for class pass
        group_ids = OrganizationSubscriptionGroupSubscription.objects.filter(
            organization_subscription = organization_subscription
        ).values_list('organization_subscription_group__id', flat=True)
        # group_ids = []
        # for group in qs_groups:
        #     group_ids.append(group.id)

        # Get permissions for groups
        qs_permissions = ScheduleItemOrganizationSubscriptionGroup.objects.filter(
            organization_subscription_group__in = group_ids
        )

        permissions = {}
        for schedule_item_organization_subscription_group in qs_permissions:
            schedule_item_id = schedule_item_organization_subscription_group.schedule_item_id

            if schedule_item_id not in permissions:
                permissions[schedule_item_id] = {}

            if schedule_item_organization_subscription_group.enroll:
                permissions[schedule_item_id]['enroll'] = True

            if schedule_item_organization_subscription_group.shop_book:
                permissions[schedule_item_id]['shop_book'] = True

            if schedule_item_organization_subscription_group.attend:
                permissions[schedule_item_id]['attend'] = True

        return permissions

    def subscription_attend_allowed(self, account_subscription):
        """
        Returns True is a class pass is allowed for a class,
        otherwise False
        """
        permissions = self.subscription_class_permissions(account_subscription)

        schedule_item_ids = []
        for schedule_item_id in permissions:
            try:
                if permissions[schedule_item_id]['attend']:
                    schedule_item_ids.append(schedule_item_id)
            except KeyError:
                pass

        return schedule_item_ids

    def subscription_attend_allowed_for_class(self, account_subscription, schedule_item):
        """
        :return: True if a subscription has the attend permission for a class
        """
        classes_allowed = self.subscription_attend_allowed(account_subscription)

        if schedule_item.id in classes_allowed:
            return True
        else:
            return False

    def subscription_shop_book_allowed(self, account_subscription):
        """
        Returns True is a class pass is allowed for a class,
        otherwise False
        """
        permissions = self.subscription_class_permissions(account_subscription)

        schedule_item_ids = []
        for schedule_item_id in permissions:
            try:
                if permissions[schedule_item_id]['shop_book']:
                    schedule_item_ids.append(schedule_item_id)
            except KeyError:
                pass

        return schedule_item_ids

    def subscription_shop_book_allowed_for_class(self, account_subscription, schedule_item):
        """
        :return: True if a classpass has the attend permission for a class
        """
        classes_allowed = self.subscription_shop_book_allowed(account_subscription)

        if schedule_item.id in classes_allowed:
            return True
        else:
            return False

    def subscription_enroll_allowed(self, account_subscription):
        """
        Returns True is a class pass is allowed for a class,
        otherwise False
        """
        permissions = self.subscription_class_permissions(account_subscription)

        schedule_item_ids = []
        for schedule_item_id in permissions:
            try:
                if permissions[schedule_item_id]['enroll']:
                    schedule_item_ids.append(schedule_item_id)
            except KeyError:
                pass

        return schedule_item_ids

    def subscription_enroll_allowed_for_class(self, account_subscription, schedule_item):
        """
        Returns True if enrollment using the given subscription is allowed for a class,
        otherwise False
        """
        classes_allowed = self.subscription_enroll_allowed(account_subscription)

        if schedule_item.id in classes_allowed:
            return True
        else:
            return False
