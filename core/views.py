import random

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from django.middleware.csrf import get_token
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes

from .models import Peca, Look, RegistroDiario
from .serializers import PecaSerializer, LookSerializer, RegistroDiarioSerializer


# ---------------------------------------------------------------- AUTH

@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def csrf(request):
    return Response({'csrfToken': get_token(request)})


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def cadastrar_usuario(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')

    if not username or not password:
        return Response({'erro': 'Usuário e senha são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'erro': 'Este nome de usuário já está em uso.'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, password=password, email=email)
    login(request, user)
    return Response({'mensagem': 'Usuário cadastrado com sucesso!', 'user': {'id': user.id, 'username': user.username}})


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def login_usuario(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return Response({'mensagem': 'Login realizado!', 'user': {'id': user.id, 'username': user.username}})
    return Response({'erro': 'Usuário ou senha inválidos.'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([AllowAny])
def logout_usuario(request):
    logout(request)
    return Response({'mensagem': 'Logout realizado com sucesso!'})


@api_view(['GET'])
@permission_classes([AllowAny])
def usuario_atual(request):
    if request.user.is_authenticated:
        return Response({'autenticado': True, 'user': {'id': request.user.id, 'username': request.user.username}})
    return Response({'autenticado': False})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def alterar_senha(request):
    senha_atual = request.data.get('senha_atual')
    nova_senha = request.data.get('nova_senha')

    if not nova_senha:
        return Response({'erro': 'Informe a nova senha.'}, status=status.HTTP_400_BAD_REQUEST)

    if not request.user.check_password(senha_atual):
        return Response({'erro': 'Senha atual incorreta.'}, status=status.HTTP_400_BAD_REQUEST)

    request.user.set_password(nova_senha)
    request.user.save()
    login(request, request.user)
    return Response({'mensagem': 'Senha alterada com sucesso!'})



class PecaViewSet(viewsets.ModelViewSet):
    serializer_class = PecaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Peca.objects.filter(usuario_django=self.request.user).order_by('-id')

    def perform_create(self, serializer):
        serializer.save(usuario_django=self.request.user)



CATEGORIAS_SUPERIORES = Q(categoria__icontains='camis') | Q(categoria__icontains='blusa') | \
    Q(categoria__icontains='top') | Q(categoria__icontains='casaco') | \
    Q(categoria__icontains='jaqueta') | Q(categoria__icontains='suéter') | Q(categoria__icontains='sueter')

CATEGORIAS_CALCADOS = Q(categoria__icontains='sapato') | Q(categoria__icontains='salto') | \
    Q(categoria__icontains='tenis') | Q(categoria__icontains='tênis') | \
    Q(categoria__icontains='sandalia') | Q(categoria__icontains='calcado') | \
    Q(categoria__icontains='calçado') | Q(categoria__icontains='bota')

CATEGORIAS_INFERIORES = Q(categoria__icontains='calça') | Q(categoria__icontains='calca') | \
    Q(categoria__icontains='short') | Q(categoria__icontains='saia')


class LookViewSet(viewsets.ModelViewSet):
    serializer_class = LookSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Look.objects.filter(usuario_django=self.request.user).order_by('-id')

    def perform_create(self, serializer):
        serializer.save(usuario_django=self.request.user)

    @action(detail=False, methods=['post'])
    def gerar_look(self, request):
        clima_filtro = request.data.get('clima', 'Geral')
        user = request.user

        pecas_base = Peca.objects.filter(usuario_django=user)

        if clima_filtro != 'Geral':
            pecas_usuario = pecas_base.filter(
                Q(clima__iexact=clima_filtro) |
                Q(clima__iexact='Geral') |
                Q(clima__iexact='Gerais') |
                Q(clima__iexact='Todos') |
                Q(clima__isnull=True) |
                Q(clima='')
            )
        else:
            pecas_usuario = pecas_base

        superiores = list(pecas_usuario.filter(CATEGORIAS_SUPERIORES))
        inferiores = list(pecas_usuario.filter(CATEGORIAS_INFERIORES).exclude(CATEGORIAS_CALCADOS))
        calcados = list(pecas_usuario.filter(CATEGORIAS_CALCADOS))

        if len(superiores) + len(inferiores) + len(calcados) < 2:
            return Response(
                {"erro": f"Não há peças suficientes cadastradas para o clima '{clima_filtro}'. Cadastre peças com esse clima!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        looks_gerados = []
        combinacoes_vistas = set()
        tentativas = 0

        while len(looks_gerados) < 3 and tentativas < 25:
            tentativas += 1
            pecas_selecionadas = []

            if superiores:
                pecas_selecionadas.append(random.choice(superiores))
            if inferiores:
                pecas_selecionadas.append(random.choice(inferiores))
            if calcados:
                pecas_selecionadas.append(random.choice(calcados))

            if len(pecas_selecionadas) < 2:
                continue

            ids_combo = tuple(sorted(p.id for p in pecas_selecionadas))
            if ids_combo in combinacoes_vistas:
                continue
            combinacoes_vistas.add(ids_combo)

            nomes_pecas = " & ".join((p.categoria or '').capitalize() for p in pecas_selecionadas)
            nome_look = f"Opção {len(looks_gerados) + 1} ({clima_filtro}) - {nomes_pecas}"
            descricao = "Sugestão de look completo: " + ", ".join(
                f"{p.categoria} ({p.cor})" for p in pecas_selecionadas
            ) + "."

            novo_look = Look.objects.create(usuario_django=user, nome_look=nome_look, descricao=descricao)
            novo_look.pecas.add(*pecas_selecionadas)

            looks_gerados.append({
                "id": novo_look.id,
                "nome_look": nome_look,
                "descricao": descricao,
                "pecas": [
                    {
                        "id": p.id,
                        "categoria": p.categoria,
                        "cor": p.cor,
                        "imagem": request.build_absolute_uri(p.imagem.url) if p.imagem else None,
                    }
                    for p in pecas_selecionadas
                ],
            })

        if not looks_gerados:
            return Response(
                {"erro": "Não foi possível gerar combinações com as peças disponíveis."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"looks": looks_gerados, "look": looks_gerados[0]})



class RegistroDiarioViewSet(viewsets.ModelViewSet):
    serializer_class = RegistroDiarioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RegistroDiario.objects.filter(usuario_django=self.request.user).order_by('-id')

    def perform_create(self, serializer):
        serializer.save(usuario_django=self.request.user)