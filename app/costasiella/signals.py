from django.contrib.auth import get_user_model
from django.dispatch import receiver

from allauth.account.signals import user_signed_up

@receiver(user_signed_up)
def new_signup(request, user, **kwargs):
    print("received sign up signal")
    
