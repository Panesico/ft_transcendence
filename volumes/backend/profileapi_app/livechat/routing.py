from django.urls import re_path
from .consumers import ChatConsumer


# Cualquier conexión a ws://<tu_dominio>/ws/chat/ será manejada por este patrón.
websocket_urlpatterns = [
    re_path(r'ws/chat/$', ChatConsumer.as_asgi()),
]