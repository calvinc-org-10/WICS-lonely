import django
from django.conf import settings as django_settings

from django_support.settings import INSTALLED_APPS, DATABASES


def setup_django_ORM():
    django_settings.configure(
        INSTALLED_APPS = INSTALLED_APPS, 
        DATABASES = DATABASES,
    )
    django.setup()
