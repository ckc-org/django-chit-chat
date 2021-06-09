from django.test import TestCase

from django.contrib.gis.geos import Point

from testapp.factories import LocationFactory


class TestFactories(TestCase):
    def test_location_factory_point_works(self):
        location = LocationFactory()
        assert location.geo_point.x
        assert location.geo_point.y

        location = LocationFactory(geo_point=Point(x=50, y=50))
        assert location.geo_point.x == 50
        assert location.geo_point.y == 50
