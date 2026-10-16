from django.contrib import admin
from .models import Usuario, Peca, Look, RegistroDiario

@admin.register(Peca)
class PecaAdmin(admin.ModelAdmin):
    exclude = ('usuario', 'usuario_django')

    def save_model(self, request, obj, form, change):
        obj.usuario_django = request.user
        try:
            perfil_usuario, created = Usuario.objects.get_or_create(
                email=request.user.email if request.user.email else f"{request.user.username}@exemplo.com",
                defaults={'nome': request.user.username}
            )
            obj.usuario = perfil_usuario
        except Exception:
            pass
        super().save_model(request, obj, form, change)


@admin.register(Look)
class LookAdmin(admin.ModelAdmin):
    exclude = ('usuario', 'usuario_django')

    def save_model(self, request, obj, form, change):
        obj.usuario_django = request.user
        try:
            perfil_usuario, created = Usuario.objects.get_or_create(
                email=request.user.email if request.user.email else f"{request.user.username}@exemplo.com",
                defaults={'nome': request.user.username}
            )
            obj.usuario = perfil_usuario
        except Exception:
            pass
        super().save_model(request, obj, form, change)


@admin.register(RegistroDiario)
class RegistroDiarioAdmin(admin.ModelAdmin):
    exclude = ('usuario', 'usuario_django')

    def save_model(self, request, obj, form, change):
        obj.usuario_django = request.user
        try:
            perfil_usuario, created = Usuario.objects.get_or_create(
                email=request.user.email if request.user.email else f"{request.user.username}@exemplo.com",
                defaults={'nome': request.user.username}
            )
            obj.usuario = perfil_usuario
        except Exception:
            pass
        super().save_model(request, obj, form, change)


admin.site.register(Usuario)