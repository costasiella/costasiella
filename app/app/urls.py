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
from django.urls import include, path
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

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
    path('d/accounts/signup/', views.CSSignUpView.as_view(), name="account_signup"),
    path('d/accounts/', include('allauth.urls')),  # allauth
    path('d/csrf/', views.csrf, name="csrf"),
    path('d/email/verified/', views.CSEmailVerifiedView.as_view(
        template_name="email_verfied.html"),
         name="email_verified"
         ),
    path('d/export/finance_payment_batch/csv/<str:node_id>',
         views.export_csv_finance_payment_batch,
         name="export_csv_finance_payment_batch"),
    path('d/export/terms-and-conditions', views.terms_and_conditions, name="terms_and_conditions"),
    path('d/export/privacy-policy', views.privacy_policy, name="privacy_policy"),
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
    path('d/export/invoice/pdf/<str:node_id>', views.invoice_pdf, name="export_invoice_pdf"),
    path('d/export/invoice/pdf/preview/<str:node_id>', views.invoice_pdf_preview, name="export_invoice_pdf_preview"),
    path('d/graphql/', jwt_cookie(GraphQLView.as_view(graphiql=True)), name="graphql"),
    path('d/mollie/webhook/', csrf_exempt(views.mollie_webhook), name="mollie_webhook"),
    path('d/update/', views.update, name="update"),
    path('d/setup/', views.setup, name="setup"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Development only
