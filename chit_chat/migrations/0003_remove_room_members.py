# Generated by Django 3.2.5 on 2022-03-31 22:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chit_chat', '0002_room_members_temp'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='room',
            name='members',
        ),
    ]