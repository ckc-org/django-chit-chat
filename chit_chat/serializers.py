from django.contrib.auth import get_user_model
from django.db.models import Count
from rest_framework import serializers, exceptions

from chit_chat.models import Room, Message
from .utils import PrimaryKeyWriteSerializerReadField


User = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = (
            'id',
            'text',
            'created_when',
            'room',
            'user',
            'users_who_viewed',
        )


class ChatUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'avatar',
        )


class RoomSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(read_only=True, many=True)
    members = PrimaryKeyWriteSerializerReadField(
        queryset=User.objects.all(),
        read_serializer=ChatUserSerializer,
        many=True,
    )

    class Meta:
        model = Room
        fields = (
            'id',
            'messages',
            'members',
        )

    def validate_members(self, users):
        requestor = self.context['request'].user
        non_requestor_users = [user for user in users if user != requestor]
        if len(non_requestor_users) < 1:
            raise exceptions.ValidationError('Must contain at least one user other than the requestor in this list.')
        non_requestor_users.append(requestor)
        return users

    def create(self, validated_data):
        member_pks = [member.pk for member in validated_data['members']]
        room = Room.objects.filter(members__in=member_pks).annotate(member_count=Count('members')).filter(member_count=len(member_pks)).first()
        return room or super().create(validated_data)
