from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

from core.views import (
    csrf,
    cadastrar_usuario,
    login_usuario,
    logout_usuario,
    usuario_atual,
    alterar_senha,
    PecaViewSet,
    LookViewSet,
    RegistroDiarioViewSet,
)

router = DefaultRouter()
router.register(r'pecas', PecaViewSet, basename='pecas')
router.register(r'looks', LookViewSet, basename='looks')
router.register(r'diario', RegistroDiarioViewSet, basename='diario')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/csrf/', csrf, name='csrf'),
    path('api/auth/cadastrar/', cadastrar_usuario, name='cadastrar'),
    path('api/auth/login/', login_usuario, name='login'),
    path('api/auth/logout/', logout_usuario, name='logout'),
    path('api/auth/me/', usuario_atual, name='usuario_atual'),
    path('api/auth/alterar-senha/', alterar_senha, name='alterar_senha'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)