from rest_framework import viewsets, mixins
from django.db.models import Max

from chit_chat.models import Room
from chit_chat.serializers import RoomSerializer


class RoomViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def get_queryset(self):
        qs = super().get_queryset().filter(members=self.request.user)
        qs = qs.annotate(latest_message_time=Max('messages__created_when')).order_by('-latest_message_time')
        qs = qs.prefetch_related(
            'messages',
            'messages__users_who_viewed',
            'members',
        )
        return qs
