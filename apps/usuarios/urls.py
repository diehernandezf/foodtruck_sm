from django.urls import path
from apps.usuarios import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.ir_login, name='login'),
    path('registro', views.ir_registro, name='registro'),
    path('crud_usuarios', views.ir_crud_usuarios, name='crud_usuarios'),
]