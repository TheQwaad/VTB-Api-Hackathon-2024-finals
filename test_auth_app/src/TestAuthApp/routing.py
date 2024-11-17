from django.urls import path
from base.consumers.tonconnect_consumer import TonConnectConsumer

websocket_urlpatterns = [
    path('ws/tonconnect/<int:user_id>/', TonConnectConsumer.as_asgi()),
]