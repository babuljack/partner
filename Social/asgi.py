import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter,URLRouter
from channels.auth import AuthMiddlewareStack
from message.routing import ws_urls
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Social.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    'websocket':AllowedHostsOriginValidator(
        AuthMiddlewareStack(
        URLRouter(
            ws_urls
        )
    )
)
})
