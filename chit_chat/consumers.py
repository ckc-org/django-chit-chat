import json

from rest_framework import exceptions
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from chit_chat.consumer_serializers import ContentSerializer
from .ckc_conf import chat_settings


def async_validation_exception_handler(func):
    async def inner(*args, **kwargs):
        self = args[0]
        assert AsyncWebsocketConsumer in self.__class__.__mro__
        try:
            return await func(*args, **kwargs)
        except exceptions.ValidationError as e:
            errors = e.detail
            if 'non_field_errors' not in errors:
                errors = {'field_errors': errors}
            await self.send(text_data=json.dumps(errors))
        except Exception as e:  # pragma: no cover
            await self.send(text_data=json.dumps({'non_field_errors': ['System Error']}))
            raise e
    return inner


class ChatRoomConsumer(AsyncWebsocketConsumer):
    MESSAGE_TYPES = [
        'chat',
    ]

    async def connect(self):
        user = self.scope['user']
        if not user.is_authenticated:
            await self.close()
            return

        await self.enter_rooms()

        # Allows us to easily send targeted messages to this user throughout the app.
        await self.channel_layer.group_add(f'user-{user.pk}', self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        user = self.scope['user']
        if user.is_authenticated:
            await self.exit_rooms()
            await self.channel_layer.group_discard(f'user-{user.pk}', self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        user = self.scope['user']
        if bytes_data is not None:
            text_data = bytes_data.decode()
        try:
            data = json.loads(text_data)
        except json.decoder.JSONDecodeError:
            await self.send(text_data=json.dumps({'non_field_errors': ['Invalid JSON.']}))
            return

        valid = await self.validate_content(data)
        if valid:
            message_type = data.get('message_type')

            if message_type == 'chat':
                data['user'] = user.pk

                if message := await self.validate_chat_message(data):
                    await self.channel_layer.group_send(
                        str(message.room.pk),
                        {
                            'type': 'chat',
                            'user': user.pk,
                            'room': message.room.pk,
                            'text': message.text,
                            'time': message.created_when.isoformat(),
                            'id': message.id,
                            # Attach the user who sent it as someone who has already viewed it
                            'users_who_viewed': [user.pk],
                        }
                    )

    async def enter_rooms(self):
        for pk in await self.get_chat_room_pks(self.scope['user']):
            await self.channel_layer.group_add(str(pk), self.channel_name)

    async def exit_rooms(self):
        for pk in await self.get_chat_room_pks(self.scope['user']):
            await self.channel_layer.group_discard(str(pk), self.channel_name)

    @async_validation_exception_handler
    async def validate_content(self, data):
        serializer = ContentSerializer(ChatRoomConsumer.MESSAGE_TYPES, data=data)
        return serializer.is_valid(raise_exception=True)

    @async_validation_exception_handler
    @database_sync_to_async
    def validate_chat_message(self, data):
        serializer = chat_settings['SERIALIZERS'].MESSAGE(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    async def chat(self, event):
        await self.send(
            text_data=json.dumps({
                'type': 'chat',
                'user': event.get('user'),
                'text': event.get('text'),
                'room': event.get('room'),
                'time': event.get('time'),
                'id': event.get('id'),
                'users_who_viewed': event.get('users_who_viewed'),
            })
        )

    async def refresh_group_add(self, _):
        await self.enter_rooms()

    @database_sync_to_async
    def get_chat_room_pks(self, user):
        return list(user.chat_rooms.values_list('pk', flat=True))
