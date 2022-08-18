django-chit-chat [<img src="https://ckcollab.com/assets/images/badges/badge.svg" alt="CKC" height="20">](https://ckcollab.com)
==========
chat for projects we help maintain @ [ckc](https://ckcollab.com)


## installing

```bash
pip install django-chit-chat
```

```python
# settings.py
INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",

    # ... add chit_chat
    "chit_chat",
)
```

```python
# routing.py
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

import chit_chat.routing


application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            chit_chat.routing.websocket_urlpatterns
        )
    ),
})
```

```python
# urls.py
from rest_framework import routers

from chit_chat.viewsets import RoomViewSet


router = routers.SimpleRouter()
router.register('chatrooms', RoomViewSet)

urlpatterns = router.urls
```

```html
<!-- chat.html -->

<script>
    // Open a connection to django-chit-chat
    YourWebsocketThing.open(`wss://${window.location.host}/ws/chatroom/`)
    
    // Write messages to screen as they're sent/received
    YourWebsocketThing.onmessage(msg => writeMessageToScreen(JSON.parse(msg.data)))
    
    // You can do a GET to "/api/chatrooms/" for a list of chatrooms + messages
    $.get("/api/chat/rooms").success(d => ...)
    
    // Send a message
    function send_message(text) {
        WSClient.send(JSON.stringify({
            message_type: "chat",
            room: 1, // ID of chat room
            text: text
        }))
    }
</script>
```


## tests

```bash
$ docker build -t django-chit-chat . && docker run django-chit-chat pytest
```


## Releasing

1. Update version number in `setup.cfg`.
2. [Create release using Github's UI](https://github.com/ckc-org/django-chit-chat/releases/new). 
   - Click the `Choose a tag` dropdown and create a new tag with the new version number.
   - Click the `Generate release notes` button to automatically create release notes.
   - This will trigger an action to build and push the release to PyPi.

