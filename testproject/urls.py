from rest_framework import routers

from testapp.viewsets import TestModelWithACreatorViewSet, TestModelWithADifferentNamedCreatorViewSet


router = routers.SimpleRouter()
router.register(r'creators', TestModelWithACreatorViewSet)
router.register(r'creators-alternative', TestModelWithADifferentNamedCreatorViewSet)

urlpatterns = router.urls
