from django.urls import path, re_path
from . import consumersCalcPongLocal, consumersCalcPongRemote

websocket_urlpatterns = [
    path('pongcalc_consumer/local/', consumersCalcPongLocal.PongCalcLocal.as_asgi()),
    path('pongcalc_consumer/remote/', consumersCalcPongRemote.PongCalcRemote.as_asgi()),
    # re_path(r'pongcalc_consumer/$', consumers.PongCalcConsumer.as_asgi()),
]
