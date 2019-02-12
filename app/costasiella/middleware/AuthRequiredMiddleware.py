class AuthRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        
        excempt_urls = [
            'account_login',
            'account_reset_password',
            'account_signup',
            'account_reset_password_done',
            'account_reset_password_from_key',
            'api_graphql'
        ]

        if request.user.is_anonymous:
            from django.urls import resolve
            current_url = resolve(request.path_info).url_name
            print('current_url')
            print(current_url)
            if not current_url in excempt_urls:
                from django.urls import reverse
                from django.shortcuts import redirect
                return redirect(reverse('account_login'))

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
