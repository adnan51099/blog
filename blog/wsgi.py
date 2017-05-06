"""
WSGI config for blog project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

path = '/home/adnan56/blog'

if path not in sys.path:
	sys.path.append(path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blog.settings")

application = get_wsgi_application()
from whitenoise.django import DjangoWhiteNoise
application = DjangoWhiteNoise(application)

#from django.contrib.staticfiles.handlers import StaticFilesHandler
#application = StaticFilesHandler(get_wsgi_application())
