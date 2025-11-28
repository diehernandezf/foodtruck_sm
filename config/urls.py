from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.productos.urls')),
    path('pagos/', include('apps.pagos.urls')),
    path('usuarios/', include('apps.usuarios.urls')),
    path('ordenes/', include('apps.ordenes.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
]