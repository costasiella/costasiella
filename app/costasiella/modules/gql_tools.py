from collections import namedtuple
from graphql_relay.node.node import from_global_id

from .messages import Messages

m = Messages()

# Auth
def require_login(user):
    if user.is_anonymous:
        raise Exception(m.user_not_logged_in)

def require_permission(user, permission):
    if not user.has_perm(permission):
        raise Exception(m.user_permission_denied)

def require_login_and_permission(user, permission):
    require_login(user)
    require_permission(user, permission)
    

# To convert relay node id to real id
def get_rid(global_id):
    Rid = namedtuple('Rid', 'name id')
    return Rid(*from_global_id(global_id))