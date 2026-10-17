from rest_framework import serializers
from .models import Peca, Look, RegistroDiario


class PecaSerializer(serializers.ModelSerializer):
    imagem = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Peca
        fields = ['id', 'categoria', 'cor', 'estilo', 'clima', 'imagem']


class LookSerializer(serializers.ModelSerializer):
    pecas = PecaSerializer(many=True, read_only=True)

    class Meta:
        model = Look
        fields = ['id', 'nome_look', 'descricao', 'pecas']


class RegistroDiarioSerializer(serializers.ModelSerializer):
    pecas_detalhes = PecaSerializer(source='pecas', many=True, read_only=True)
    pecas = serializers.PrimaryKeyRelatedField(
        many=True, required=False, queryset=Peca.objects.none()
    )

    class Meta:
        model = RegistroDiario
        fields = ['id', 'data', 'pecas', 'pecas_detalhes', 'observacao', 'avaliacao', 'comentario']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            self.fields['pecas'].child_relation.queryset = Peca.objects.filter(
                usuario_django=request.user
            )