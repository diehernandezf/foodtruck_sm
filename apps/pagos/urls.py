from django.urls import path
from apps.pagos import views

app_name = 'pagos'

urlpatterns = [
    path('iniciar_pago/', views.iniciar_pago, name='iniciar_pago'),
    path('retorno_pago/', views.retorno_pago, name='retorno_pago'),
]