from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.ir_login, name='login'), # LoginView es una vista predeterminada de django para iniciar sesion
    path('logout/', views.ir_logout, name='logout'), # igual que LogoutView, sus templates van en una ruta especifica
    path('registro/', views.ir_registro, name='registro'),
    path('crud_usuarios/', views.dashboard, name='crud_usuarios'),
]