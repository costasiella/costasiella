from django.utils.translation import gettext as _

from ..models import OrganizationClasspassGroupClasspass, ScheduleItemOrganizationClasspassGroup


class ClassCheckinDude():
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

        
