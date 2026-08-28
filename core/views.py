from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Peca, Look, Usuario
from .serializers import UsuarioSerializer, PecaSerializer, LookSerializer
import random

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class PecaViewSet(viewsets.ModelViewSet):
    queryset = Peca.objects.all().order_by('-id')
    serializer_class = PecaSerializer

    def perform_create(self, serializer):
        file_obj = self.request.FILES.get('imagem') or self.request.FILES.get('imagem_path')
        if file_obj:
            serializer.save(imagem=file_obj)
        else:
            serializer.save()

class LookViewSet(viewsets.ModelViewSet):
    queryset = Look.objects.all().order_by('-id')
    serializer_class = LookSerializer

    @action(detail=False, methods=['post'])
    def gerar_look(self, request):
        clima_filtro = request.data.get('clima', 'Geral')
        pecas_usuario = Peca.objects.all()

        if clima_filtro != 'Geral':
            pecas_usuario = pecas_usuario.filter(clima__iexact=clima_filtro)

        superiores = pecas_usuario.filter(categoria__icontains='camis') | pecas_usuario.filter(categoria__icontains='blusa') | pecas_usuario.filter(categoria__icontains='top')
        inferiores = pecas_usuario.filter(categoria__icontains='calça') | pecas_usuario.filter(categoria__icontains='short') | pecas_usuario.filter(categoria__icontains='saia')

        if not superiores.exists() or not inferiores.exists():
            pecas_lista = list(pecas_usuario)
            if len(pecas_lista) < 2:
                return Response(
                    {"erro": "Cadastre pelo menos 2 peças para gerar um look!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            peca_top = pecas_lista[0]
            peca_bottom = pecas_lista[1]
        else:
            peca_top = random.choice(list(superiores))
            peca_bottom = random.choice(list(inferiores))

        pecas_do_look = [
            {
                "id": peca_top.id,
                "categoria": peca_top.categoria,
                "cor": peca_top.cor,
                "imagem": request.build_absolute_uri(peca_top.imagem.url) if peca_top.imagem else None
            },
            {
                "id": peca_bottom.id,
                "categoria": peca_bottom.categoria,
                "cor": peca_bottom.cor,
                "imagem": request.build_absolute_uri(peca_bottom.imagem.url) if peca_bottom.imagem else None
            }
        ]

        nome_look = f"Look {clima_filtro} - {peca_top.categoria.capitalize()} & {peca_bottom.categoria.capitalize()}"
        descricao = f"Sugestão de look: {peca_top.categoria} ({peca_top.cor}) combinada com {peca_bottom.categoria} ({peca_bottom.cor})."

        novo_look = Look.objects.create(
            nome_look=nome_look,
            descricao=descricao
        )
        novo_look.pecas.add(peca_top, peca_bottom)

        return Response({
            "look": {
                "id": novo_look.id,
                "nome_look": nome_look,
                "descricao": descricao,
                "pecas": pecas_do_look
            }
        })