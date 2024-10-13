from django.urls import path, re_path
from .consumers import FormConsumer
from . import consumerProxyPongLocal, consumerProxyPongRemote, consumerMainRoom

websocket_urlpatterns = [
    path('wss/calcgame/game/local/', consumerProxyPongLocal.ProxyCalcGameLocal.as_asgi()),
    path('wss/calcgame/pong/remote/', consumerProxyPongRemote.ProxyPongCalcRemote.as_asgi()),
    path('wss/calcgame/cows/remote/', consumerProxyPongRemote.ProxyPongCalcRemote.as_asgi()),
    # re_path(r'wss/calcgame/pong/$', consumerCalcGame.PongCalcConsumer.as_asgi()),

    # Friend Invite suggestion
    path('wss/inviteafriend', FormConsumer.as_asgi()),
    path('wss/inviteafriend/', FormConsumer.as_asgi()),

    # Main room
    path('wss/mainroom/<int:user_id>/', consumerMainRoom.mainRoom.as_asgi()),
    # re_path(r'ws/somepath/$', consumers.YourConsumer.as_asgi()),
]
