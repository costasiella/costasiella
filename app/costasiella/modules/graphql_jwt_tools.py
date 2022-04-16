"""
We probably don't need it, but for some reason the middleware doesn't seem to pass users properly with the current
versions. So it can be here for now, until it's fixed upstream.
Everything below here can be deleted again once request.user returns something.

"""

from graphql_jwt.utils import get_credentials, get_payload, get_user_by_payload


def get_user_by_token(token, context=None):
    payload = get_payload(token, context)
    return get_user_by_payload(payload)


def get_user_from_cookie(request, **kwargs):
    user = None
    token = get_credentials(request, **kwargs)
    if token is not None:
        user = get_user_by_token(token, request)

    return user
