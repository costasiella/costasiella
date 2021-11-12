from django.utils.translation import gettext as _
from django.views.static import serve
from django.http import HttpResponse
from graphql_jwt.exceptions import JSONWebTokenError

from ..modules.graphql_jwt_tools import get_user_by_token


def serve_protected_file(request, path, token, document_root=None, show_indexes=False):
    """
    Authenticate user using token before serving a file
    :param request: Django request
    :param path: path of requisted file
    :param token: JWT
    :param document_root: settings.MEDIA_ROOT
    :param show_indexes: Don't show indexes, only included here for clarity, should always be False!
    :return:
    """
    try:
        user = get_user_by_token(token, request)
        if user:
            return serve(request, path, document_root, show_indexes)
    except JSONWebTokenError as e:
        return HttpResponse(_('Please sign in to view this file'), status=401)

    return HttpResponse(_('Please sign in to view this file'), status=401)
