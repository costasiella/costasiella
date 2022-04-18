from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie

# Return csrf token in JSON data
# def csrf(request):
#     return JsonResponse({'csrfToken': get_token(request)})

# Set csrf token in Cookie
@ensure_csrf_cookie
def csrf(request):
    return JsonResponse({'success': 'CSRF cookie set'})
