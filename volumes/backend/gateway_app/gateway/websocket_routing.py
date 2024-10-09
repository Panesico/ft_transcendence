from django.urls import path, re_path
from .consumers import FormConsumer
from . import consumerCalcGame

websocket_urlpatterns = [
    path('wss/calcgame/pong/', consumerCalcGame.PongCalcConsumer.as_asgi()),
    # re_path(r'wss/calcgame/pong/$', consumerCalcGame.PongCalcConsumer.as_asgi()),

    path('wss/inviteafriend', FormConsumer.as_asgi()),
    path('wss/inviteafriend/', FormConsumer.as_asgi()),
    # re_path(r'ws/somepath/$', consumers.YourConsumer.as_asgi()),
]
