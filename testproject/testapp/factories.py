import random
import string

import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

from chit_chat.models import Room, Message


User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    email = factory.LazyAttribute(lambda x: f'test_user{"".join(random.sample(string.ascii_letters, 8))}@{"".join(random.sample(string.ascii_letters, 8))}.com')


class RoomFactory(DjangoModelFactory):
    class Meta:
        model = Room

    @factory.post_generation
    def members(self, created, extracted):
        if not created:
            if extracted:
                raise ValueError('Cannot set members on RoomFactory if using .build()')
            return
        self.save()
        for user in extracted if extracted else [UserFactory() for _ in range(random.randint(1, 5))]:
            self.members.add(user)


class MessageFactory(DjangoModelFactory):
    class Meta:
        model = Message
    text = factory.Faker('text')
    user = factory.SubFactory(UserFactory)
    room = factory.SubFactory(RoomFactory)
