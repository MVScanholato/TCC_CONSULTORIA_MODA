from rest_framework import serializers
from .models import Peca, Look, Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
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