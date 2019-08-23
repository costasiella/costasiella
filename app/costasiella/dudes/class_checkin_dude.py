from django.utils.translation import gettext as _

from ..models import OrganizationClasspassGroupClasspass, ScheduleItemAttendance, ScheduleItemOrganizationClasspassGroup

class ClassCheckinDude():
    def _class_checkedin(self, account, schedule_item, date):
        """
        :return: schedule_item_attendance object if found, so we can check for reviews
        """
        schedule_item_attendance = ScheduleItemAttendance.objects.filter(
            account=account,
            schedule_item=schedule_item,
            date=date
        )
        
        return schedule_item_attendance


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
        # Check if not already signed in
        qs = self._class_checkedin(account, schedule_item, date)
        print(qs)
        if qs.exists():
            # Already signed in, check for review check-in
            schedule_item_attendance = qs.first()

            if not schedule_item_attendance == 'REVIEW':
                raise Exception(_('This account is already checked in to this class'))
            # else:
            #TODO: Write review check-ins code

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
            attendance_type = "CLASSPASS",
            account = account,
            account_classpass = account_classpass,
            schedule_item = schedule_item,
            date = date,
            online_booking = online_booking,
            booking_status = booking_status
        )

        schedule_item_attendance.save()

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


        return dict(status=status, message=message)

    # def classpass_class_permissions(self, account_classpass, public_only=True):
    def classpass_class_permissions(self, account_classpass):
        """
        :return: return list of class permissons
        """
        organization_classpass = account_classpass.organization_classpass

        # Get groups for class pass
        qs_groups = OrganizationClasspassGroupClasspass.objects.filter(
            organization_classpass = organization_classpass
        )
        group_ids = []
        for group in qs_groups:
            group_ids.append(group.id)

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


    def classpass_shop_book_allowed(self, acount_classpass):
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
