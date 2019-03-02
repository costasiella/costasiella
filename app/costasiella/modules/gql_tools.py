

def require_login(user):
    if user.is_anonymous:
        raise Exception('Not logged in!')

def require_permission(user, permission):
    if not user.has_perm(permission):
        raise Exception('Permission denied!')

def require_login_and_permission(user, permission):
    require_login(user)
    require_permission(user, permission)
    