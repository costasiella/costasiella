from .messages import Messages

m = Messages()

def require_login(user):
    if user.is_anonymous:
        raise Exception(m.user_not_logged_in)

def require_permission(user, permission):
    if not user.has_perm(permission):
        raise Exception(m.user_permission_denied)

def require_login_and_permission(user, permission):
    require_login(user)
    require_permission(user, permission)
    