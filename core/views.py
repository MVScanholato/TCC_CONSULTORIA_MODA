from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
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
        # Retorna apenas as peças do usuário logado (ou todas se for superuser/sem login para testes)
        if self.request.user.is_authenticated:
            return Peca.objects.filter(usuario_django=self.request.user).order_by('-id')
        return Peca.objects.all().order_by('-id')

    def perform_create(self, serializer):
        file_obj = self.request.FILES.get('imagem') or self.request.FILES.get('imagem_path')

        # Atribui o usuário logado à peça
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
            pecas_usuario = Peca.objects.filter(usuario_django=request.user)
        else:
            pecas_usuario = Peca.objects.all()

        if clima_filtro != 'Geral':
            pecas_usuario = pecas_usuario.filter(clima__iexact=clima_filtro)

        superiores = pecas_usuario.filter(categoria__icontains='camis') | pecas_usuario.filter(
            categoria__icontains='blusa') | pecas_usuario.filter(categoria__icontains='top')
        inferiores = pecas_usuario.filter(categoria__icontains='calça') | pecas_usuario.filter(
            categoria__icontains='short') | pecas_usuario.filter(categoria__icontains='saia')

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

        user = request.user if request.user.is_authenticated else None
        novo_look = Look.objects.create(
            usuario_django=user,
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
        login(request, request.user)  # Mantém o usuário logado após mudar a senha
        return Response({'mensagem': 'Senha alterada com sucesso!'})