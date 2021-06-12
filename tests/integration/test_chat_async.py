import pytest
from django.contrib.sessions.models import Session
from django.contrib.auth import HASH_SESSION_KEY, SESSION_KEY, BACKEND_SESSION_KEY, get_user_model
from django.conf import settings
from django.test import override_settings
from channels.routing import get_default_application
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from asyncio.exceptions import TimeoutError

from chit_chat.consumers import ChatRoomConsumer
from testproject.testapp.factories import RoomFactory, UserFactory
from testproject.testapp.serializers import ChatTestSerializer

User = get_user_model()


@pytest.mark.django_db
@database_sync_to_async
def create_user(auth_backend=None):
    user = UserFactory()
    session_store = Session.get_session_store_class()()
    session_store[HASH_SESSION_KEY] = user.get_session_auth_hash()
    session_store[SESSION_KEY] = str(user.pk)
    backends = settings.AUTHENTICATION_BACKENDS
    if len(backends) > 1:  # pragma: no cover
        raise ValueError('Only one authentication backend should be set or else the auth_backend kwarg is required.')
    session_store[BACKEND_SESSION_KEY] = auth_backend or backends[0]
    session_store.create()
    return user, session_store.session_key


@pytest.mark.django_db
@database_sync_to_async
def create_room(**kwargs):
    return RoomFactory(**kwargs)


@pytest.mark.django_db
@database_sync_to_async
def get_messages_from_room(room):
    return list(room.messages.all().order_by('created_when').select_related('user'))


async def create_websocket_communicator(session_id):
    communicator = WebsocketCommunicator(
        get_default_application(),
        '/ws/chatroom/',
        headers=[('cookie'.encode(), f'sessionid={session_id}'.encode())]
    )
    connected, subprotocol = await communicator.connect(timeout=5)
    assert connected
    return communicator


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_connection_to_chat_room_requires_session_cookie():
    communicator = WebsocketCommunicator(get_default_application(), '/ws/chatroom/')
    connected, subprotocol = await communicator.connect(timeout=5)
    assert not connected

    user, session_key = await create_user()
    communicator = await create_websocket_communicator(session_key)
    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_user_is_able_to_connect_and_send_message_after_disconnecting():
    user, session_key = await create_user()
    room = await create_room(members=[user])
    assert len(await get_messages_from_room(room)) == 0
    communicator = await create_websocket_communicator(session_key)
    await communicator.send_json_to({'message_type': 'chat', 'room': room.pk, 'text': 'hello'})

    resp = await communicator.receive_json_from()

    messages = await get_messages_from_room(room)
    assert len(messages) == 1
    assert messages[0].text == 'hello'
    assert messages[0].user == user

    assert resp['text'] == messages[0].text
    assert resp['time']

    await communicator.disconnect()

    communicator = await create_websocket_communicator(session_key)
    await communicator.send_json_to({'message_type': 'chat', 'room': room.pk, 'text': 'hello 2'})

    resp = await communicator.receive_json_from(timeout=3)

    messages = await get_messages_from_room(room)
    assert len(messages) == 2
    assert messages[1].text == 'hello 2'
    assert messages[1].user == user

    assert resp['text'] == messages[1].text
    assert resp['time']

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_send_message_creates_new_message_object():
    user, session_key = await create_user()
    room = await create_room(members=[user])
    assert len(await get_messages_from_room(room)) == 0
    communicator = await create_websocket_communicator(session_key)
    await communicator.send_json_to({'message_type': 'chat', 'room': room.pk, 'text': 'hello'})

    resp = await communicator.receive_json_from()

    messages = await get_messages_from_room(room)
    assert len(messages) == 1
    assert messages[0].text == 'hello'
    assert messages[0].user == user

    assert resp['text'] == messages[0].text
    assert resp['user'] == user.pk
    assert resp['time']

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_serializer_hook():
    user, session_key = await create_user()
    room = await create_room(members=[user])
    assert len(await get_messages_from_room(room)) == 0
    communicator = await create_websocket_communicator(session_key)
    await communicator.send_json_to({'message_type': 'chat', 'room': room.pk, 'text': 'hello'})

    resp = await communicator.receive_json_from()
    resp.pop('time')
    assert resp == {'room': room.pk, 'text': 'hello', 'type': 'chat', 'user': user.pk}

    ckc_chat_settings = {
        'CHAT_MESSAGE_SERIALIZER': ChatTestSerializer,
    }
    with override_settings(CKC_CHAT_SERIALIZERS=ckc_chat_settings):
        await communicator.send_json_to({'message_type': 'chat', 'room': room.pk, 'text': 'hello'})
        resp = await communicator.receive_json_from(timeout=3)
        assert resp == {'field_errors': {'text': [ChatTestSerializer.text_error]}}

    ckc_chat_settings['CHAT_MESSAGE_SERIALIZER'] = 'testapp.serializers.ChatTestSerializer'

    with override_settings(CKC_CHAT_SERIALIZERS=ckc_chat_settings):
        await communicator.send_json_to({'message_type': 'chat', 'room': room.pk, 'text': 'hello'})
        resp = await communicator.receive_json_from()
        assert resp == {'field_errors': {'text': [ChatTestSerializer.text_error]}}

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_cannot_send_message_with_invalid_type():
    user, session_key = await create_user()
    room = await create_room(members=[user])
    communicator = await create_websocket_communicator(session_key)
    await communicator.send_json_to({'message_type': 'invalid', 'room': room.pk, 'text': 'hello'})

    resp = await communicator.receive_json_from()
    assert resp == {'field_errors': {'message_type': [f'Must be one of the following message types: {ChatRoomConsumer.MESSAGE_TYPES}']}}

    messages = await get_messages_from_room(room)
    assert len(messages) == 0

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_cannot_send_message_to_room_that_user_is_not_a_member_of():
    user, session_key = await create_user()
    room = await create_room(members=[user])
    other_room = await create_room()
    communicator = await create_websocket_communicator(session_key)
    await communicator.send_json_to({'message_type': 'chat', 'room': other_room.pk, 'text': 'hello'})

    resp = await communicator.receive_json_from(timeout=3)
    assert resp == {'non_field_errors': ['Cannot send messages to chat rooms that you are not a member of.']}

    messages = await get_messages_from_room(other_room)
    assert len(messages) == 0

    messages = await get_messages_from_room(room)
    assert len(messages) == 0

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_invalid_json_returns_useful_error_message():
    user, session_key = await create_user()
    room = await create_room(members=[user])
    communicator = await create_websocket_communicator(session_key)
    await communicator.send_to(bytes_data=b"hola\0")

    resp = await communicator.receive_json_from(timeout=5)
    assert resp == {'non_field_errors': ['Invalid JSON.']}

    messages = await get_messages_from_room(room)
    assert len(messages) == 0

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_chat_message_proliferates_to_correct_chatroom():
    print(settings.CHANNEL_LAYERS)
    user, session_key = await create_user()
    other_user, other_session_key = await create_user()
    room = await create_room(members=[user, other_user])
    communicator = await create_websocket_communicator(session_key)
    other_communicator = await create_websocket_communicator(other_session_key)

    # Make sure that a user in a different room does not get the message
    unrelated_user, unrelated_session_key = await create_user()
    await create_room(members=[unrelated_user])
    unrelated_communicator = await create_websocket_communicator(unrelated_session_key)

    # User sends message
    await communicator.send_json_to({'message_type': 'chat', 'room': room.pk, 'text': 'hello'})

    # Other user receives message
    response = await other_communicator.receive_json_from()
    assert response['user'] == user.pk
    assert response['room'] == room.pk

    # User also receives message
    response = await communicator.receive_json_from()
    assert response['user'] == user.pk
    assert response['room'] == room.pk

    # This user should not receive a message
    try:
        await unrelated_communicator.receive_json_from()
    except TimeoutError:
        pass

    await communicator.disconnect()
    await other_communicator.disconnect()
