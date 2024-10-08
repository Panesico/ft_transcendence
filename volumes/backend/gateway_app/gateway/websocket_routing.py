from django.urls import path, re_path
from .consumers import FormConsumer
from . import consumerGameCalc

websocket_urlpatterns = [
    path('wss/calcgame/pong/', consumerGameCalc.PongCalcConsumer.as_asgi()),
    # re_path(r'wss/calcgame/pong/$', consumerGameCalc.PongCalcConsumer.as_asgi()),

    path('wss/profileapi', FormConsumer.as_asgi()),
    path('wss/profileapi/', FormConsumer.as_asgi()),
    # re_path(r'ws/somepath/$', consumers.YourConsumer.as_asgi()),
]
