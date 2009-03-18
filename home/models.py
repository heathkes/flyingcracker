from django.db import models

# No models created here yet.
# This file is imported by home/views.py and sets up a connection
# for django-registration signal.

from registration.models import RegistrationManager
from registration.signals import user_activated
from serviceclient.models import ServiceClientUserProfile as SCUP
from serviceclient.models import ServiceClient

def create_SCUP(sender, **kwargs):
    user = kwargs.get('user')
    service_client = ServiceClient.objects.get(name='cracklyfinger.com')
    scup = SCUP(user=user, service_client=service_client, user_type=SCUP.NORMAL_TYPE, active=True)
    scup.save()

user_activated.connect(create_SCUP)
