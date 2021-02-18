"""
WSGI config for collectanea project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os, django

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'collectanea.settings.base')
# os.environ["DJANGO_SETTINGS_MODULE"] = "collectanea.settings.base"
# django.setup()
application = get_wsgi_application()
