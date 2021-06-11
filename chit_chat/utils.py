from rest_framework import serializers


#  TODO: This should be stored in the django-ckc package
class PrimaryKeyWriteSerializerReadField(serializers.PrimaryKeyRelatedField):
    def __init__(self, *args, **kwargs):
        read_serializer = kwargs.pop('read_serializer', None)
        assert read_serializer is not None, (
            'PrimaryKeyWriteSerializerReadField must provide `read_serializer` argument.'
        )
        super().__init__(*args, **kwargs)
        self.read_serializer = read_serializer

    # Related fields will not look up any of the object's values for normal primary
    # key serialization. This override forces the lookup of the entire object.
    def use_pk_only_optimization(self):
        return False

    def to_representation(self, value):
        return self.read_serializer(value, context=self.context).data
