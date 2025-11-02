from django.contrib import admin
from django.urls import path, include
from apps.productos.views import ir_inicio, ir_crud_productos

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.productos.urls')),
    path('pagos/', include('apps.pagos.urls')),
    path('usuarios/', include('apps.usuarios.urls')),
]