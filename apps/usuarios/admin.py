from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from .models import UsuarioPersonalizado

from .forms import UsuarioCreationForm, UsuarioChangeForm

@admin.register(UsuarioPersonalizado)
class UsuarioPersonalizadoAdmin(UserAdmin):
    add_form = UsuarioCreationForm      # formulario al crear
    form = UsuarioChangeForm            # formulario al editar
    model = UsuarioPersonalizado

    list_display = ("username", "email", "first_name", "last_name", "telefono", "total_pedidos", "is_staff", "is_active")
    search_fields = ("username", "email", "first_name", "last_name", "telefono")
    ordering = ("username",)

    # Secciones al EDITAR
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Información personal", {"fields": ("first_name", "last_name", "email", "telefono")}),
        ("Permisos", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Fechas importantes", {"fields": ("last_login", "date_joined")}),
    )

    # Secciones al CREAR
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username",
                "first_name", "last_name", "email", "telefono",
                "password1", "password2",
                "is_active", "is_staff", "is_superuser", "groups",
            ),
        }),
    )