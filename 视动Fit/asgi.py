"""
ASGI config for 视动Fit project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

# 视动Fit/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import 视动Fit.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '视动Fit.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            视动Fit.routing.websocket_urlpatterns
        )
    ),
})
