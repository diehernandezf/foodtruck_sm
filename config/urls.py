from django.contrib import admin
from django.urls import path, include
from apps.productos.views import ir_inicio

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ir_inicio, name='inicio'),
    path('carrito/', include('apps.productos.urls')),
    path('pagos/', include('apps.pagos.urls')),
]