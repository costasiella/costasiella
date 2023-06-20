from django.contrib.auth.models import Group, Permission

class PermissionDude:
    def __init__(self):
        """
        Fetch current version from SysSettings
        """
        self.selfcheckin_permissions = [
            'view_account',
            'view_accountclasspass',
            'view_accountsubscription',
            'view_organizationclasspass',
            'view_organizationlocation',
            'view_organizationlocationroom',
            'view_organizationsubscription',
            'view_scheduleitemattendance',
            'add_scheduleitemattendance',
            'change_scheduleitemattendance',
            'delete_scheduleitemattendance',
            'view_scheduleitem',
            'view_selfcheckin',
        ]

    def _verify_admin_group_permissions(self):
        """
        Grant any missing permissions to the admins group
        :return:
        """
        all_permissions = Permission.objects.all()
        try:
            admin_group = Group.objects.get(id=100)
            if admin_group:
                for permission in all_permissions:
                    if permission not in admin_group.permissions.all():
                        admin_group.permissions.add(permission)
        except Group.DoesNotExist:
            pass

    def _verify_selfcheckin_permissions(self):
        """
        Verify that the selfcheckin group has all required permissions
        :return:
        """
        all_permissions = []
        try:
            selfcheckin_group = Group.objects.get(id=99)
            for permission_string in self.selfcheckin_permissions:
                permission = Permission.objects.get(codename=permission_string)
                if permission not in selfcheckin_group.permissions.all():
                    selfcheckin_group.permissions.add(permission)
        except Group.DoesNotExist:
            pass


    def verify_system_permissions(self):
        """
        Set predefined permissions for a few commonly used groups
        :return:
        """
        self._verify_admin_group_permissions()
        self._verify_selfcheckin_permissions()

