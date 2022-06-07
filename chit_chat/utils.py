from collections import OrderedDict

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

    def to_representation(self, value, pk_only=False):
        if pk_only:
            # Returning just the PK so dropdowns can render this as an option in DRF browsable API
            return value.pk
        else:
            # Returning full dict representation for reading normally
            return self.read_serializer(value, context=self.context).data

    def get_choices(self, cutoff=None):
        """Overriding this base method to change to_representation so it passes pk_only=True"""
        queryset = self.get_queryset()
        if queryset is None:
            # Ensure that field.choices returns something sensible
            # even when accessed with a read-only field.
            return {}

        if cutoff is not None:
            queryset = queryset[:cutoff]

        return OrderedDict([
            (
                self.to_representation(item, pk_only=True),
                self.display_value(item)
            )
            for item in queryset
        ])
