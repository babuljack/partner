from django.urls import path
from .consumer import ChatConsumer
ws_urls=[
 path('chat/<chat_name>',ChatConsumer.as_asgi()),
]
