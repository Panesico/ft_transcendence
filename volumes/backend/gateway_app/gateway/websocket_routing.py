from django.urls import path, re_path
from .consumers import FormConsumer
from . import consumerPongLocal, consumerPongRemote, consumerMainRoom

websocket_urlpatterns = [
    path('wss/calcgame/pong/local/', consumerPongLocal.ProxyPongCalcLocal.as_asgi()),
    path('wss/calcgame/pong/remote/', consumerPongRemote.ProxyPongCalcRemote.as_asgi()),
    # re_path(r'wss/calcgame/pong/$', consumerCalcGame.PongCalcConsumer.as_asgi()),

    # Friend Invite suggestion
    path('wss/inviteafriend', FormConsumer.as_asgi()),
    path('wss/inviteafriend/', FormConsumer.as_asgi()),

    # Main room
    path('wss/mainroom/<int:user_id>/', consumerMainRoom.mainRoom.as_asgi()),
    # re_path(r'ws/somepath/$', consumers.YourConsumer.as_asgi()),
]
