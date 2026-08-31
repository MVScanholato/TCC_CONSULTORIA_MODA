from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from core.views import (
    PecaViewSet, LookViewSet,
    cadastrar_usuario, login_usuario, logout_usuario, usuario_atual
)

router = DefaultRouter()
router.register(r'pecas', PecaViewSet, basename='peca')
router.register(r'looks', LookViewSet, basename='look')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/cadastrar/', cadastrar_usuario),
    path('api/auth/login/', login_usuario),
    path('api/auth/logout/', logout_usuario),
    path('api/auth/me/', usuario_atual),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)