"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings

from graphene_django.views import GraphQLView
from graphql_jwt.decorators import jwt_cookie

from costasiella import views

# Development only
from django.conf import settings
from django.conf.urls.static import static
# Development only end

urlpatterns = [
    # path('', login_required(TemplateView.as_view(template_name="backend.html")), name="home"),
    # path('', TemplateView.as_view(template_name="backend.html"), name="home"),
    path('d/admin/', admin.site.urls),
    path('d/admin/defender/', include('defender.urls')),  # defender admin
    # override of email view to add user profile context data
    path('d/accounts/confirm-email/',
         views.CSEmailVerificationSentView.as_view(),
         name="account_emailverificationsent"),
    path('d/accounts/password/reset/', views.CSPasswordResetView.as_view(), name="account_passwordreset"),
    path('d/accounts/password/reset/done/', views.CSPasswordResetDoneView.as_view(),
         name="account_passwordresetdone"),
    path('d/accounts/signup/', views.CSSignUpView.as_view(), name="account_signup"),
    path('d/accounts/', include('allauth.urls')),  # allauth
    path('d/csrf/', views.csrf, name="csrf"),
    path('d/email/verified/', views.CSEmailVerifiedView.as_view(
        template_name="email_verfied.html"),
         name="email_verified"
         ),
    path('d/export/account_data/',
         views.export_account_data,
         name="export_account_data"),
    path('d/export/finance_expenses/excel/<str:date_from>/<str:date_until>',
         views.export_excel_finance_expenses,
         name="export_excel_finance_expenses"),
    path('d/export/finance_payment_batch/csv/<str:node_id>',
         views.export_csv_finance_payment_batch,
         name="export_csv_finance_payment_batch"),
    path('d/export/terms-and-conditions', views.terms_and_conditions, name="terms_and_conditions"),
    path('d/export/privacy-policy', views.privacy_policy, name="privacy_policy"),
    path('d/export/relations/accounts/active',
         views.export_excel_accounts_active,
         name="export_excel_accounts_active"),
    path('d/export/insight/classpasses/active/<int:year>',
         views.export_excel_insight_classpasses_active,
         name="export_excel_insight_classpasses_active"),
    path('d/export/insight/classpasses/sold/<int:year>',
         views.export_excel_insight_classpasses_sold,
         name="export_excel_insight_classpasses_sold"),
    path('d/export/insight/subscriptions/active/<int:year>',
         views.export_excel_insight_subscriptions_active,
         name="export_excel_insight_classpasses_active"),
    path('d/export/insight/subscriptions/sold/<int:year>',
         views.export_excel_insight_subscriptions_sold,
         name="export_excel_insight_subscriptions_sold"),
    path('d/export/insight/subscriptions/stopped/<int:year>',
         views.export_excel_insight_subscriptions_stopped,
         name="export_excel_insight_subscriptions_stopped"),
    path('d/export/insight/subscriptions/paused/<int:year>',
         views.export_excel_insight_subscriptions_paused,
         name="export_excel_insight_subscriptions_paused"),
    path('d/export/insight/subscriptions/blocked/<int:year>',
         views.export_excel_insight_subscriptions_blocked,
         name="export_excel_insight_subscriptions_blocked"),
    path('d/export/invoice/pdf/<str:node_id>', views.invoice_pdf, name="export_invoice_pdf"),
    path('d/export/invoice/pdf/preview/<str:node_id>', views.invoice_pdf_preview,
         name="export_invoice_pdf_preview"),
    path('d/export/invoices/<str:date_from>/<str:date_until>/<str:status>',
         views.export_excel_finance_invoices,
         name="export_invoices"),
    path('d/export/quote/pdf/<str:node_id>', views.quote_pdf, name="export_quote_pdf"),
    path('d/export/quote/pdf/preview/<str:node_id>', views.quote_pdf_preview,
         name="export_invoice_pdf_preview"),
    path('d/export/quotes/<str:date_from>/<str:date_until>/<str:status>/',
         views.export_excel_finance_quotes,
         name="export_quotes"),
    path('d/export/schedule_event/activities/attendance/<str:schedule_event_node_id>',
         views.export_excel_schedule_event_activities_attendance,
         name="export_schedule_event_activities_attendance"),
    path('d/export/schedule_item_attendance/mailinglist/<str:schedule_item_node_id>/<str:date>',
         views.export_excel_schedule_item_attendance_mailinglist,
         name="export_schedule_item_mailinglist"),
    path('d/graphql/', jwt_cookie(GraphQLView.as_view(graphiql=settings.DEBUG)), name="graphql"),
    # graphql_app path is meant for apps, it uses header authentication
    # "Authorization": "JWT <token"> instead of cookie authentication and doesn't require a csrf token.
    # This path can also be used instead of the one above to troubleshoot CSRF issues... do I have one or not?
    path('d/graphql_app/', csrf_exempt(GraphQLView.as_view(graphiql=settings.DEBUG)), name="graphql"),
    path('d/mollie/webhook/', csrf_exempt(views.mollie_webhook), name="mollie_webhook"),
    path('d/update/', views.update, name="update"),
    path('d/setup/', views.setup, name="setup"),
    re_path(r'^%s(?P<path>.*)' % settings.MEDIA_PROTECTED_PUBLIC_URL[1:],
            views.serve_protected_file, name="media_protected")
]

# Static files through Django dev server for development environment
if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_PROTECTED_PUBLIC_URL, document_root=settings.MEDIA_PROTECTED_ROOT)
