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
    try:
        if request.method == 'POST':
            # Obtenemos el carrito de la sesión o creamos uno nuevo
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key

            carrito = Carrito.objects.filter(session_key=session_key).first()

            if not carrito:
                return JsonResponse({'error': 'No hay un carrito activo'}, status=400)

            if not carrito.items.exists():
                return JsonResponse({'error': 'El carrito está vacío'}, status=400)

            total = carrito.total
            if total <= 0:
                return JsonResponse({'error': 'El monto total debe ser mayor a 0'}, status=400)

            buy_order = generar_orden()
            return_url = request.build_absolute_uri(reverse('pagos:retorno_pago'))

            try:
                tx = get_transaction()
                response = tx.create(buy_order, session_key, round(total), return_url)

                carrito.token = response['token']
                carrito.save()

                return JsonResponse({
                    'success': True,
                    'url': response['url'], 
                    'token': response['token']
                })
            except Exception as e:
                return JsonResponse({
                    'error': f'Error al procesar el pago: {str(e)}',
                    'success': False
                }, status=500)

        return JsonResponse({'error': 'Método no permitido'}, status=405)
    except Exception as e:
        return JsonResponse({
            'error': f'Error inesperado: {str(e)}',
            'success': False
        }, status=500)

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