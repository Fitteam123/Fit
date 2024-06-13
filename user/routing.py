from django.urls import re_path
from user import consumers

websocket_urlpatterns = [
    re_path(r'ws/output/$', consumers.OutputConsumer.as_asgi()),
]