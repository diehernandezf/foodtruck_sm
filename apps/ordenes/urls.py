from django.urls import path
from apps.ordenes import views

app_name = 'ordenes'

urlpatterns = [
    path('', views.ir_miPedido, name='miPedido')
]