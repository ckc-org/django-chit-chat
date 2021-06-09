from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from testapp.models import ModelWithACreator, ModelWithADifferentNamedCreator

User = get_user_model()


class TestDefaultUserCreateMixin(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="test", password="test")
        self.client.force_authenticate(self.user)

    def test_default_create_user_mixin_works(self):
        from django.urls import get_resolver
        print(get_resolver().reverse_dict.keys())

        resp = self.client.post(reverse('modelwithacreator-list'))
        print(resp.content)
        assert resp.status_code == 201
        assert ModelWithACreator.objects.get(created_by=self.user)

    def test_default_create_user_mixin_with_different_field_name_works(self):
        resp = self.client.post(reverse('modelwithadifferentnamedcreator-list'))
        assert resp.status_code == 201
        assert ModelWithADifferentNamedCreator.objects.get(owner=self.user)
