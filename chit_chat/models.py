from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import models


User = get_user_model()


class Room(models.Model):
    members = models.ManyToManyField(User, related_name='chat_rooms', through='RoomMembership')
    created_when = models.DateTimeField(default=timezone.now)


class RoomMembership(models.Model):
    room = models.ForeignKey(Room, related_name='memberships', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='chat_room_memberships', on_delete=models.CASCADE)
    archived = models.BooleanField(default=False)
    ignore_notifications = models.BooleanField(default=False)
    created_when = models.DateTimeField(default=timezone.now)


class Message(models.Model):
    text = models.TextField()
    room = models.ForeignKey(Room, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='chat_room_messages', on_delete=models.CASCADE)
    created_when = models.DateTimeField(default=timezone.now)
    users_who_viewed = models.ManyToManyField(User, related_name='chat_room_messages_viewed')

    def __str__(self):
        return f"Sent by User.id = {self.user_id} @ {self.created_when:%I:%M%p}"
