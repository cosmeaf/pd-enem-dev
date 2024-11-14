from rest_framework.viewsets import ModelViewSet
from .models import UserProfile, Address, AcademicData
from .serializers import UserProfileSerializer, AddressSerializer, AcademicDataSerializer
from django.http import JsonResponse
from django.core.cache import cache

class UserProfileViewSet(ModelViewSet):
    queryset = UserProfile.objects.select_related('address', 'academic_data').all()
    serializer_class = UserProfileSerializer

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()


class AddressViewSet(ModelViewSet):
    queryset = Address.objects.select_related('user_profile').all()
    serializer_class = AddressSerializer

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()


class AcademicDataViewSet(ModelViewSet):
    queryset = AcademicData.objects.select_related('user_profile').all()
    serializer_class = AcademicDataSerializer

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()




def redis_test(request):
    cache.set('test_key', 'test_value', timeout=30)
    value = cache.get('test_key')
    return JsonResponse({'cached_value': value})
