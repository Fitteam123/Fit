"""
ASGI config for 视动Fit project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

import websoc
from websoc.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "视动Fit.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websoc.routing.websocket_urlpatterns
        )
    ),
})
