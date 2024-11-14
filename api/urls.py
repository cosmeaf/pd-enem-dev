from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserProfileViewSet, 
    AddressViewSet, 
    AcademicDataViewSet,
    redis_test
)

router = DefaultRouter()
router.register(r'userprofiles', UserProfileViewSet)
router.register(r'addresses', AddressViewSet)
router.register(r'academicdata', AcademicDataViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('redis-test/', redis_test),
]
