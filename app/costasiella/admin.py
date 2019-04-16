from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

# Register your models here.

from .forms import AccountCreationForm, AccountChangeForm

class AccountAdmin(UserAdmin):
    add_form = AccountCreationForm
    form = AccountChangeForm
    model = get_user_model()
    list_display = ['email', ]

admin.site.register(get_user_model(), AccountAdmin)