from django.urls import re_path
from .consumer import ChatConsumer
ws_urls=[
re_path(r'chat/(?P<chat_name>\w+)/$',ChatConsumer.as_asgi()),
]
