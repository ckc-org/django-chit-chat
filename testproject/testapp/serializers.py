from rest_framework import serializers

from chit_chat.consumer_serializers import ChatMessageSerializer


class ChatTestSerializer(ChatMessageSerializer):
    text_error = "Ah ah ah. You didn't say the magic word."

    def validate_text(self, text):
        if text == 'hello':
            raise serializers.ValidationError(ChatTestSerializer.text_error)
