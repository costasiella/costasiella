from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

from .models import Account


class AccountCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = get_user_model()
        fields = ('email',)


class AccountChangeForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = ('email',)


class SignupForm(forms.Form):
    first_name = forms.CharField(
        max_length=30, 
        widget=forms.TextInput(attrs={'placeholder': _('First name')}),
        label=_('First name')
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'placeholder': _('Last name')}), 
        label=_('Last name')
    )

    def signup(self, request, user):
        # Username field is set in the save function of the account model
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
