from django.urls import path
from apps.productos import views

app_name = 'productos'

urlpatterns = [
    path('', views.ir_inicio, name='home'),
    path('carrito/agregar/', views.agregar_al_carrito, name='agregar'),
    path('carrito/ver/', views.ver_carrito, name='ver'),
    path('carrito/actualizar/', views.actualizar_cantidad, name='actualizar'),
    path('carrito/eliminar/', views.eliminar_del_carrito, name='eliminar'),
    path('carrito/vaciar/', views.vaciar_carrito, name='vaciar'),
]