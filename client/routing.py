# routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/user/$", consumers.BaseConsumer.as_asgi()),
    re_path(r"ws/worker/$", consumers.OrderNotificationConsumer.as_asgi()),
    re_path(r"ws/client/$", consumers.ClientNotificationConsumer.as_asgi()),
]
