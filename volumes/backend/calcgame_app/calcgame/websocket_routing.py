from django.urls import path, re_path
from . import consumers

websocket_urlpatterns = [
    # path('wss/calcgame/pong/', consumers.PongCalcConsumer.as_asgi()),
    # re_path(r'wss/calcgame/pong/$', consumers.PongCalcConsumer.as_asgi()),
    path('wss/calcgame/pong/', consumers.PongCalcConsumer.as_asgi()),
    # re_path(r'ws/calcgame/pong/$', consumers.CalcgameConsumer.as_asgi()),
    # re_path(r'calcgame_consumer/$', consumers.CalcgameConsumer.as_asgi()),
    # re_path(r'wss/calcgame/$', consumers.GameConsumer.as_asgi()),
]
