# mysite/asgi.py
import django
django.setup()
import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import chat.routing 

from django.core.management import call_command

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")


application = ProtocolTypeRouter({
  "http": get_asgi_application(),
  "websocket": AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})
