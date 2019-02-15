

def require_login_or_permission(user, permission):
    if user.is_anonymous:
        raise Exception('Not logged in!')

    if not user.has_perm(permission):
        raise Exception('Permission denied!')