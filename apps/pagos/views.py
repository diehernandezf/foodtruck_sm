import json
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
from apps.ordenes.models import Carrito, Pedido, DetallePedido
from django.contrib.auth import get_user_model

    # """Create a Transaction using WebpayOptions constructed from Django settings.

    # The installed Transbank SDK exposes WebpayOptions/Options; older code referenced
    # WebpayPlus.default_* attributes which are not present in this SDK version.
    # Use settings.TRANSBANK_COMMERCE_CODE and settings.TRANSBANK_API_KEY instead.
    # """
    
    # Map environment string to IntegrationType if desired; default to TEST for development
def get_transaction():
    commerce_code = getattr(settings, 'TRANSBANK_COMMERCE_CODE', None)
    api_key = getattr(settings, 'TRANSBANK_API_KEY', None)
    integration = IntegrationType.TEST # Modo de pruebas
    options = WebpayOptions(commerce_code, api_key, integration)
    return Transaction(options)

# (esto evita que django valide el token cuando se hace una request desde el token a la vista)
@csrf_exempt
def iniciar_pago(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            delivery = data.get('delivery', 0)
            carrito = obtener_carrito(request)

            if not carrito:
                return JsonResponse({'error': 'No hay un carrito activo'}, status=400)

            if not carrito.items.exists():
                return JsonResponse({'error': 'El carrito está vacío'}, status=400)

            carrito.delivery = delivery
            

            total = carrito.total
            if total <= 0:
                return JsonResponse({'error': 'El monto total debe ser mayor a 0'}, status=400)

            buy_order = generar_orden() # Genera orden unica
            return_url = request.build_absolute_uri(reverse('pagos:retorno_pago'))

            try:
                tx = get_transaction()
                response = tx.create(buy_order, carrito.session_key, round(total), return_url) # crea una transaccion en Webpay

                carrito.token = response['token']
                carrito.save() # Guarda token en el carrito

                return JsonResponse({ # retorna pago exitoso, la url a webpay y el token
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
def retorno_pago(request): # Maneja el retorno despues del pago con Webpay Plus
    token = request.POST.get('token_ws') or request.GET.get('token_ws')

    tx = get_transaction()
    response = tx.commit(token) # consulta a transbank el resultado final del pago

    # falta actualizar el registro en sqlite(aprobado o fallido)
    if response['status'] == 'AUTHORIZED': # confirma que el pago fue exitoso
        carrito = Carrito.objects.filter(token=token).first() # guarda el carrito asociado al token
        if carrito:
            carrito.pagado = True   
            carrito.activo = False
            carrito.save()

            # Creamos el pedido
            pedido = Pedido.objects.create(
                usuario = carrito.usuario,
                token = token,
                total = carrito.total,
                estado = 'pagado',
                codigo_autorizacion = response.get('authorization_code', ''),
                orden_compra = response.get('buy_order', '')
            )
            
            # Creamos detalle del pedido (copiamos items del carrito)
            for item in carrito.items.all():
                DetallePedido.objects.create(
                    pedido = pedido,
                    producto = item.producto,
                    nombre_producto = item.producto.nombre,
                    cantidad = item.cantidad,
                    precio_unitario = item.producto.precio,
                    subtotal = item.cantidad * item.producto.precio
                )

        return render(request, 'exito.html', {'response': response, 'pedido':pedido})
    else:
        return render(request, 'error.html', {'response': response})

def generar_orden():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

def obtener_carrito(request):
    """
    Recupera o crea el carrito 'abierto' para:
    - Usuario autenticado: por campo 'usuario'
    - Usuario anónimo: por 'session_key'
    Usa tus campos reales: 'usuario', 'activo', 'pagado'
    """
    # Asegura session_key
    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key

    # Si está autenticado, prioriza carrito por usuario
    if request.user.is_authenticated:
        carrito = Carrito.objects.filter(usuario=request.user, activo=True, pagado=False).first()
        if carrito:
            # Sincroniza session_key si cambió
            if carrito.session_key != session_key:
                carrito.session_key = session_key
                carrito.save(update_fields=['session_key'])
            return carrito

        # Si no hay por usuario, intenta por session_key actual (anónimo) y "elevarlo"
        carrito = Carrito.objects.filter(session_key=session_key, activo=True, pagado=False).first()
        if carrito:
            carrito.usuario = request.user
            carrito.save(update_fields=['usuario'])
            return carrito

        # No existe ninguno → crea uno nuevo para el usuario
        return Carrito.objects.create(
            usuario=request.user,
            session_key=session_key,
            activo=True,
            pagado=False
        )

    # Usuario anónimo → trabaja por session_key
    carrito = Carrito.objects.filter(session_key=session_key, activo=True, pagado=False).first()
    if carrito:
        return carrito

    # Crea carrito anónimo
    return Carrito.objects.create(
        usuario=None,
        session_key=session_key,
        activo=True,
        pagado=False
    )