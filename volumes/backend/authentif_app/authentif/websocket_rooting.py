from django.urls import path, re_path
from .consumers import InviteFriend
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

websocket_urlpatterns = [
    path('wss/invitefriends', InviteFriend.as_asgi()),
    path('wss/invitefriends/', InviteFriend.as_asgi()),
    # re_path(r'ws/somepath/$', consumers.YourConsumer.as_asgi()),
]