from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from .models import Peca, Look
from .serializers import PecaSerializer, LookSerializer, UsuarioSerializer
import random


# API de Cadastro de Usuário
@api_view(['POST'])
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


# API de Login
@api_view(['POST'])
@permission_classes([AllowAny])
def login_usuario(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return Response({'mensagem': 'Login realizado!', 'user': {'id': user.id, 'username': user.username}})
    else:
        return Response({'erro': 'Usuário ou senha inválidos.'}, status=status.HTTP_401_UNAUTHORIZED)


# API de Logout
@api_view(['POST'])
def logout_usuario(request):
    logout(request)
    return Response({'mensagem': 'Logout realizado com sucesso!'})


# API para verificar quem está logado
@api_view(['GET'])
@permission_classes([AllowAny])
def usuario_atual(request):
    if request.user.is_authenticated:
        return Response({'autenticado': True, 'user': {'id': request.user.id, 'username': request.user.username}})
    return Response({'autenticado': False})


class PecaViewSet(viewsets.ModelViewSet):
    serializer_class = PecaSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Peca.objects.filter(usuario_django=self.request.user).order_by('-id')
        return Peca.objects.all().order_by('-id')

    def perform_create(self, serializer):
        file_obj = self.request.FILES.get('imagem') or self.request.FILES.get('imagem_path')

        user = self.request.user if self.request.user.is_authenticated else None

        if file_obj:
            serializer.save(usuario_django=user, imagem=file_obj)
        else:
            serializer.save(usuario_django=user)


class LookViewSet(viewsets.ModelViewSet):
    serializer_class = LookSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Look.objects.filter(usuario_django=self.request.user).order_by('-id')
        return Look.objects.all().order_by('-id')

    @action(detail=False, methods=['post'])
    def gerar_look(self, request):
        clima_filtro = request.data.get('clima', 'Geral')

        if request.user.is_authenticated:
            pecas_base = Peca.objects.filter(usuario_django=request.user)
        else:
            pecas_base = Peca.objects.all()

        # Filtra estritamente pelo clima escolhido ou peças coringa ("Geral"/"Todos")
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

        # 1. Peças Superiores do clima correto
        superiores = pecas_usuario.filter(
            Q(categoria__icontains='camis') | Q(categoria__icontains='blusa') | Q(categoria__icontains='top') | Q(categoria__icontains='casaco') | Q(categoria__icontains='jaqueta') | Q(categoria__icontains='suéter') | Q(categoria__icontains='sueter')
        )

        # 2. Peças Inferiores do clima correto (exclui calçados)
        inferiores = pecas_usuario.filter(
            Q(categoria__icontains='calça') | Q(categoria__icontains='calca') | Q(categoria__icontains='short') | Q(categoria__icontains='saia')
        ).exclude(
            Q(categoria__icontains='sapato') | Q(categoria__icontains='salto') | Q(categoria__icontains='tenis') | Q(categoria__icontains='sandalia') | Q(categoria__icontains='calcado') | Q(categoria__icontains='calçado') | Q(categoria__icontains='bota')
        )

        # 3. Calçados DO CLIMA CORRETO apenas
        calcados = pecas_usuario.filter(
            Q(categoria__icontains='sapato') | Q(categoria__icontains='salto') | Q(categoria__icontains='tenis') | Q(categoria__icontains='tênis') | Q(categoria__icontains='sandalia') | Q(categoria__icontains='calcado') | Q(categoria__icontains='calçado') | Q(categoria__icontains='bota')
        )

        pecas_selecionadas = []

        # Seleciona 1 superior do clima correto
        if superiores.exists():
            pecas_selecionadas.append(random.choice(list(superiores)))

        # Seleciona 1 inferior do clima correto
        if inferiores.exists():
            pecas_selecionadas.append(random.choice(list(inferiores)))

        # Seleciona 1 calçado do clima correto
        if calcados.exists():
            pecas_selecionadas.append(random.choice(list(calcados)))

        # Se não houver peças suficientes cadastradas para esse clima específico
        if len(pecas_selecionadas) < 2:
            return Response(
                {"erro": f"Não há peças suficientes cadastradas para o clima '{clima_filtro}'. Cadastre peças com esse clima!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        pecas_do_look = [
            {
                "id": p.id,
                "categoria": p.categoria,
                "cor": p.cor,
                "imagem": request.build_absolute_uri(p.imagem.url) if p.imagem else None
            }
            for p in pecas_selecionadas
        ]

        nomes_pecas = " & ".join([p.categoria.capitalize() for p in pecas_selecionadas])
        nome_look = f"Look {clima_filtro} - {nomes_pecas}"

        descricoes = [f"{p.categoria} ({p.cor})" for p in pecas_selecionadas]
        descricao = f"Sugestão de look completo: {', '.join(descricoes)}."

        user = request.user if request.user.is_authenticated else None
        novo_look = Look.objects.create(
            usuario_django=user,
            nome_look=nome_look,
            descricao=descricao
        )
        novo_look.pecas.add(*pecas_selecionadas)

        return Response({
            "look": {
                "id": novo_look.id,
                "nome_look": nome_look,
                "descricao": descricao,
                "pecas": pecas_do_look
            }
        })


# API para alterar a senha
@api_view(['POST'])
def alterar_senha(request):
    if not request.user.is_authenticated:
        return Response({'erro': 'Usuário não autenticado.'}, status=status.HTTP_401_UNAUTHORIZED)

    senha_atual = request.data.get('senha_atual')
    nova_senha = request.data.get('nova_senha')

    if not request.user.check_password(senha_atual):
        return Response({'erro': 'Senha atual incorreta.'}, status=status.HTTP_400_BAD_REQUEST)

    request.user.set_password(nova_senha)
    request.user.save()
    login(request, request.user)
    return Response({'mensagem': 'Senha alterada com sucesso!'})