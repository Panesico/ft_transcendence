# mysite/routing.py

from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path, re_path
from .consumers import ChatConsumer
application = ProtocolTypeRouter({
    'websocket': URLRouter([
        path('ws/chat/', ChatConsumer.as_asgi()),
    ])
})

# make the path reusable
websocket_urlpatterns = [
  re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()),
]