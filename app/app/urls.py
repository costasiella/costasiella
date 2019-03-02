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

urlpatterns = [
    path('', login_required(TemplateView.as_view(template_name="backend.html")), name="home"),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    # path('graphql/', GraphQLView.as_view(graphiql=True)),
    path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True)), name="api_graphql"),
]



# from django.conf.urls import url
# from django.contrib import admin
# from django.views.generic import TemplateView

# urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    # url(r'^', TemplateView.as_view(template_name="index.html")),
# ]
