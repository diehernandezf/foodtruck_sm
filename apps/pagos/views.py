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
from apps.productos.views import obtener_o_crear_carrito

def get_transaction(): # Crea el cliente de Transbank
    commerce_code = getattr(settings, 'TRANSBANK_COMMERCE_CODE', None)
    api_key = getattr(settings, 'TRANSBANK_API_KEY', None)
    integration = IntegrationType.TEST # Modo de pruebas
    options = WebpayOptions(commerce_code, api_key, integration)
    return Transaction(options)

def iniciar_pago(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            direccion = data.get('direccion', '')
            carrito = obtener_o_crear_carrito(request)

            if not carrito:
                return JsonResponse({'error': 'No hay un carrito activo'}, status=400)

            if not carrito.items.exists():
                return JsonResponse({'error': 'El carrito está vacío'}, status=400)

            if direccion:
                carrito.direccion = direccion
                carrito.save()
            
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
    tbk_token = request.GET.get('TBK_TOKEN')
    tbk_orden_compra = request.GET.get('TBK_ORDEN_COMPRA')
    tbk_id_sesion = request.GET.get('TBK_ID_SESION')

    if tbk_token and not token:
        context = {
            'estado': 'anulado',
            'mensaje': 'El pago fue anulado o no se completó correctamente.',
            'tbk_orden_compra': tbk_orden_compra,
            'tbk_id_sesion': tbk_id_sesion,
        }
        return render(request, 'error.html', context)

    tx = get_transaction()
    response = tx.commit(token) # consulta a transbank el resultado final del pago

    pedido = None

    if response['status'] == 'AUTHORIZED': # confirma que el pago fue exitoso
        carrito = Carrito.objects.filter(token=token).first() # guarda el carrito asociado al token
        if carrito:
            usuario = carrito.usuario

            descuento_aplicado = carrito.descuento
            total_con_descuento = carrito.total

            carrito.pagado = True
            carrito.activo = False
            carrito.save()

            # Creamos el pedido
            pedido = Pedido.objects.create(
                usuario = usuario,
                token = token,
                total = total_con_descuento,
                estado = 'pagado',
                codigo_autorizacion = response.get('authorization_code', ''),
                orden_compra = response.get('buy_order', ''),
                delivery = carrito.delivery,
                tipo_entrega = carrito.tipo_entrega,
                direccion = carrito.direccion,
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

        return render(request, 'exito.html', {'response': response, 'pedido':pedido, 'carrito':carrito, 'descuento_aplicado':descuento_aplicado})
    else:
        return render(request, 'error.html', {'response': response})

def generar_orden():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))