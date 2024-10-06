from django.urls import path, re_path
from .consumers import FormConsumer
from . import consumerGameCalc
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

websocket_urlpatterns = [
    path('wss/gamecalc/pong/', consumerGameCalc.PongCalcConsumer.as_asgi()),
    # re_path(r'wss/gamecalc/pong/$', consumerGameCalc.PongCalcConsumer.as_asgi()),

    path('wss/profileapi', FormConsumer.as_asgi()),
    path('wss/profileapi/', FormConsumer.as_asgi()),
    # re_path(r'ws/somepath/$', consumers.YourConsumer.as_asgi()),
]
