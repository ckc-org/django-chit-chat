from django.urls import reverse

from rest_framework.test import APITestCase

from testproject.testapp.factories import RoomFactory, MessageFactory, UserFactory


class TestChat(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_room_create(self):
        room_data = {
            'members': [UserFactory().pk]
        }
        resp = self.client.post(reverse('room-list'), data=room_data)
        assert resp.status_code == 201

    def test_attempt_to_create_duplicate_rooms_results_in_original_being_returned(self):
        room_data = {
            'members': [UserFactory().pk]
        }
        resp = self.client.post(reverse('room-list'), data=room_data)
        assert resp.status_code == 201
        room_id = resp.json()['id']

        resp = self.client.post(reverse('room-list'), data=room_data)
        assert resp.status_code == 201
        assert room_id == resp.json()['id']

    def test_room_create_requires_another_user(self):
        room_data = {
            'members': [self.user.pk]
        }
        resp = self.client.post(reverse('room-list'), data=room_data)
        assert resp.status_code == 400
        assert resp.json() == {'members': ['Must contain at least one user other than the requestor in this list.']}

    def test_only_members_can_see_rooms(self):
        member_room = RoomFactory(members=[self.user])

        # Room that self.user is not a part of
        RoomFactory(members=[UserFactory()])

        resp = self.client.get(reverse('room-list'))
        assert resp.status_code == 200
        assert resp.json()['count'] == 1
        assert resp.json()['results'][0]['id'] == member_room.pk

    def test_get_room_messages(self):
        for _ in range(5):
            room = RoomFactory(members=[self.user])
            for _ in range(3):
                MessageFactory(room=room)

        resp = self.client.get(reverse('room-list'))
        assert resp.status_code == 200
        assert resp.json()['count'] == 5
        data = resp.json()['results']
        for room in data:
            assert len(room['messages']) == 3
            assert all(message['user'] for message in room['messages'])

    def test_rooms_are_ordered_by_latest_message(self):
        room_1 = RoomFactory(members=[self.user])
        MessageFactory(room=room_1)
        room_2 = RoomFactory(members=[self.user])
        MessageFactory(room=room_2)

        resp = self.client.get(reverse('room-list'))
        assert resp.status_code == 200
        assert resp.json()['count'] == 2
        data = resp.json()['results']
        assert data[0]['id'] == room_2.pk
        assert data[1]['id'] == room_1.pk

        MessageFactory(room=room_1)

        resp = self.client.get(reverse('room-list'))
        assert resp.status_code == 200
        assert resp.json()['count'] == 2
        data = resp.json()['results']
        assert data[0]['id'] == room_1.pk
        assert data[1]['id'] == room_2.pk

    def test_mark_all_messages_in_room_as_viewed(self):
        room_1 = RoomFactory(members=[self.user])
        message_1 = MessageFactory(room=room_1)
        room_2 = RoomFactory(members=[self.user])
        message_2 = MessageFactory(room=room_2)
        message_3 = MessageFactory(room=room_2)

        assert not message_1.users_who_viewed.filter(pk=self.user.pk).exists()
        assert not message_2.users_who_viewed.filter(pk=self.user.pk).exists()

        with self.assertNumQueries(5):
            resp = self.client.post(reverse('room-viewed-all-messages', args=(room_1.pk,)))
            assert resp.status_code == 200

        assert message_1.users_who_viewed.filter(pk=self.user.pk).exists()
        assert not message_2.users_who_viewed.filter(pk=self.user.pk).exists()
        assert not message_3.users_who_viewed.filter(pk=self.user.pk).exists()

        with self.assertNumQueries(5):
            resp = self.client.post(reverse('room-viewed-all-messages', args=(room_2.pk,)))
            assert resp.status_code == 200

        assert message_1.users_who_viewed.filter(pk=self.user.pk).exists()
        assert message_2.users_who_viewed.filter(pk=self.user.pk).exists()
        assert message_3.users_who_viewed.filter(pk=self.user.pk).exists()
