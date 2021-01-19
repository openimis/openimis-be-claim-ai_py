from django.urls import re_path, path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/Claim/(?P<process_id>\w+)/$', consumers.ClaimConsumer.as_asgi()),
]
