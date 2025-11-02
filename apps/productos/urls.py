from django.urls import path
from apps.productos import views

app_name = 'productos'

urlpatterns = [
    path('agregar/', views.agregar_al_carrito, name='agregar'),
    path('ver/', views.ver_carrito, name='ver'),
    path('actualizar/', views.actualizar_cantidad, name='actualizar'),
    path('eliminar/', views.eliminar_del_carrito, name='eliminar'),
    path('vaciar/', views.vaciar_carrito, name='vaciar'),
    path('', views.ir_inicio),
    path('crud_productos', views.ir_crud_productos, name='crud_productos'),
]