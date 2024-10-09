from django.urls import path, re_path
from . import consumers

websocket_urlpatterns = [
    path('pongcalc_consumer/local/', consumers.PongCalcLocal.as_asgi()),
    path('pongcalc_consumer/remote/', consumers.PongCalcRemote.as_asgi()),
    # re_path(r'pongcalc_consumer/$', consumers.PongCalcConsumer.as_asgi()),
]
