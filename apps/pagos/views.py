import os
import random
import string
from django.shortcuts import render
from django.urls import reverse

from ordenes.models import Carrito

# Create your views here.
TRANSBANK_COMMERCE_CODE = os.getenv(TRANSBANK_COMMERCE_CODE)
TRANSBANK_API_KEY = os.getenv(TRANSBANK_API_KEY)
TRANSBANK_ENVIRONMENT = os.getenv(TRANSBANK_ENVIRONMENT)

def iniciar_pago(request):
    return_url = request.build_absolute_uri(reverse('ordenes/retorno_pago'))
    if request.method == 'POST':
        carrito = Carrito(request)

def commit_pago():

def generar_orden():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

def retorno_pago():