from django.utils.translation import gettext as _
from django.views.static import serve
from django.http import HttpResponse, HttpResponseForbidden
from django.conf import settings
from graphql_jwt.exceptions import JSONWebTokenError

from ..modules.graphql_jwt_tools import get_user_from_cookie


def serve_protected_file(request, path, show_indexes=False):
    """
    Authenticate user using token before serving a file
    :param request: Django request
    :param path: path of requested file
    :param show_indexes: Don't show indexes, only included here for clarity, should always be False!
    :return:
    """
    print(path)

    try:
        user = get_user_from_cookie(request)
        if user:
            # Check path for finance_expense and perform authz check
            if not _authorization(user, path):
                return HttpResponseForbidden(_('Not authorized to access this file'))

            # For test & development?
            if settings.DEBUG:
                document_root = settings.MEDIA_PROTECTED_ROOT
                return serve(request, path, document_root, show_indexes)

            # Production
            response = HttpResponse()
            # Content-type will be detected by nginx
            del response['Content-Type']
            # response['X-Accel-Redirect'] = '/protected/media/' + path
            response['X-Accel-Redirect'] = settings.MEDIA_PROTECTED_INTERNAL_URL + path
            return response
    except JSONWebTokenError as e:
        return HttpResponseForbidden(_('Not authorized to access this file'))

    # In case something unexpected happens, just deny the request
    return HttpResponseForbidden(_('Not authorized to access this file'))

def _authorization(user, path):
    required_permission = ""

    if "finance_expense" in path:
        required_permission = "costasiella.view_financeexpense"

    return user.has_perm(required_permission)
