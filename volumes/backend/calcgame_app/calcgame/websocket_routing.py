from django.urls import path, re_path
from . import consumers

websocket_urlpatterns = [
    path('pongcalc_consumer/', consumers.PongCalcConsumer.as_asgi()),
    # re_path(r'wss/calcgame/pong/$', consumers.PongCalcConsumer.as_asgi()),
]
