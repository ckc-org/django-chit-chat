from rest_framework import viewsets, mixins, status
from django.db.models import Max, Count
from rest_framework.response import Response

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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        member_pks = [member.pk for member in data['members']]
        if room := Room.objects.filter(members__in=member_pks).annotate(member_count=Count('members')).filter(member_count=len(member_pks)).first():
            data = self.get_serializer(room).data
        else:
            self.perform_create(serializer)
            data = serializer.data
        headers = self.get_success_headers(data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)
