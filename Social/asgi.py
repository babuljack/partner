import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter,URLRouter
from channels.auth import AuthMiddlewareStack
from message.routing import ws_urls
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Social.settings')
django.setup()

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
