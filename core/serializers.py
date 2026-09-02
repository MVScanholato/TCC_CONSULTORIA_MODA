from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Peca, Look, RegistroDiario

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class PecaSerializer(serializers.ModelSerializer):
    imagem = serializers.ImageField(required=False, allow_null=True)
    imagem_path = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Peca
        fields = '__all__'
        extra_kwargs = {
            'usuario': {'required': False, 'allow_null': True}
        }

class LookSerializer(serializers.ModelSerializer):
    pecas = PecaSerializer(many=True, read_only=True)

    class Meta:
        model = Look
        fields = '__all__'

class RegistroDiarioSerializer(serializers.ModelSerializer):
    pecas_detalhes = PecaSerializer(source='pecas', many=True, read_only=True)

    class Meta:
        model = RegistroDiario
        fields = '__all__'