from rest_framework import routers

from chit_chat.viewsets import RoomViewSet


router = routers.SimpleRouter()

router.register('chatrooms', RoomViewSet)

urlpatterns = router.urls
