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


## distributing

```bash
# change version in setup.cfg
$ ./setup.py sdist
$ twine upload dist/*
```

## tests

```bash
$ docker build -t django-chit-chat . && docker run django-chit-chat pytest
```
