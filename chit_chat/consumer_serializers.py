from rest_framework import serializers, exceptions
from django.contrib.auth import get_user_model

from chit_chat.models import Room, Message


User = get_user_model()


class ContentSerializer(serializers.Serializer):
    message_type = serializers.CharField()

    def __init__(self, valid_message_types, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.valid_message_types = valid_message_types

    def validate_message_type(self, message_type):
        if message_type not in self.valid_message_types:
            raise exceptions.ValidationError(f'Must be one of the following message types: {self.valid_message_types}')
        return message_type


class ChatMessageSerializer(serializers.Serializer):
    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all())
    text = serializers.CharField()
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def validate(self, attrs):
        # Make sure the user is in the room.
        if not attrs['room'].members.filter(pk=attrs['user'].pk).exists():
            raise exceptions.ValidationError('Cannot send messages to chat rooms that you are not a member of.')
        return attrs

    def create(self, validated_data):
        message = Message.objects.create(**validated_data)

        # Add sender as viewer
        message.users_who_viewed.add(message.user)

        return message
