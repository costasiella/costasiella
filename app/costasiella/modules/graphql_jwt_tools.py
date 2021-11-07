"""
We probably don't need it, but for some reason the middleware doesn't seem to pass users properly with the current
versions. So it can be here for now, until it's fixed upstream.
Everything below here can be deleted again once request.user works.

You'll probably just want to import the "get_user_by_token" function into a view.
"""

import jwt
from graphql_jwt import exceptions
from graphql_jwt.settings import jwt_settings
from graphql_jwt.utils import get_payload, get_user_by_payload

def get_user_by_token(token, context=None):
    payload = get_payload(token, context)
    return get_user_by_payload(payload)