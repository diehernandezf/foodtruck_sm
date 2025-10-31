import os
import random
import string
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_type import IntegrationType
from transbank.common.options import WebpayOptions
from apps.ordenes.models import Carrito

    # """Create a Transaction using WebpayOptions constructed from Django settings.

    # The installed Transbank SDK exposes WebpayOptions/Options; older code referenced
    # WebpayPlus.default_* attributes which are not present in this SDK version.
    # Use settings.TRANSBANK_COMMERCE_CODE and settings.TRANSBANK_API_KEY instead.
    # """
    
    # Map environment string to IntegrationType if desired; default to TEST for development
def get_transaction():
    commerce_code = getattr(settings, 'TRANSBANK_COMMERCE_CODE', None)
    api_key = getattr(settings, 'TRANSBANK_API_KEY', None)
    integration = IntegrationType.TEST
    options = WebpayOptions(commerce_code, api_key, integration)
    return Transaction(options)

# (esto evita que django valide el token cuando se hace una request desde el token a la vista)
@csrf_exempt
def iniciar_pago(request):
    if request.method == 'POST':
        carrito = Carrito.objects.filter(usuario=request.user, activo=True).first()

        if not carrito:
            return JsonResponse({'error': 'No hay un carrito activo'}, status=400)

        total = carrito.total  # calcular a mano o llamar funcion

        buy_order = generar_orden()
        session_id = str(request.user.id)
        return_url = request.build_absolute_uri(reverse('retorno_pago'))

        tx = get_transaction()
        response = tx.create(buy_order, session_id, round(total), return_url)

        carrito.token = response['token']
        carrito.save()

        return JsonResponse({'url': response['url'], 'token': response['token']})

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@csrf_exempt
def retorno_pago(request):
    token = request.POST.get('token_ws')

    tx = get_transaction()
    response = tx.commit(token)

    if response['status'] == 'AUTHORIZED':
        carrito = Carrito.objects.filter(token=token).first()
        if carrito:
            carrito.pagado = True
            carrito.activo = False
            carrito.save()
        return render(request, 'pagos/exito.html', {'response': response})
    else:
        return render(request, 'pagos/error.html', {'response': response})

def generar_orden():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))