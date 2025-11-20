from django.urls import path
from apps.ordenes import views

app_name = 'ordenes'

urlpatterns = [
    path('', views.ir_miPedido, name='miPedido'),
    path('administrar', views.ir_administrar, name='administrar'),
    path('administrar/<int:id_pedido>/completado/',views.completar_pedido, name='completar_pedido')
]