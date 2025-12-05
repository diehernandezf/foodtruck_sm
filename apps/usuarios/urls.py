from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.ir_login, name='login'), 
    path('logout/', views.ir_logout, name='logout'), 
    path('registro/', views.ir_registro, name='registro'),
]