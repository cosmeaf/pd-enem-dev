from rest_framework import serializers
from .models import UserProfile, Address, AcademicData

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['city_name'] = instance.city_name if instance.city_name else 'Não Informado'
        return representation


class AcademicDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicData
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['apply_method'] = instance.apply_method or 'Não Informado'
        representation['score'] = instance.score or 0
        return representation


class UserProfileSerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True)
    academic_data = AcademicDataSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['preferred_name'] = instance.preferred_name if instance.preferred_name else instance.nome_completo
        representation['cel_responsavel'] = instance.cel_responsavel if instance.cel_responsavel else 'Não Informado'
        return representation
