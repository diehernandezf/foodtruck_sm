from decimal import Decimal
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from apps.ordenes.models import Carrito, Pedido
from apps.usuarios.models import UsuarioPersonalizado

from apps.productos.views import obtener_o_crear_carrito

from django.views.decorators.http import require_POST

import json

# Create your views here.

def ir_miPedido(request):
    carrito = obtener_o_crear_carrito(request)
    items = carrito.items.select_related('producto').all()
    es_primer_pedido = False
    if carrito.usuario:
        es_primer_pedido = carrito.usuario.total_pedidos == 0
    
    context = {
        'items': [
            {
                'id': item.id,
                'producto_id': item.producto.id,
                'nombre': item.producto.nombre,
                'precio_unitario': float(item.precio_unitario),
                'cantidad': item.cantidad,
                'total': float(item.total),
                'imagen_url': item.producto.imagen_url
            }
            for item in items
        ],
        'subtotal': float(carrito.subtotal),
        'descuento': float(carrito.descuento),
        'total': float(carrito.total),
        'total_items': carrito.total_items,
        'usuario': carrito.usuario,
        'delivery': float(carrito.delivery),
        'tipo_entrega': carrito.tipo_entrega,
        'es_primer_pedido': es_primer_pedido,
    }

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(context)

    return render(request, 'miPedido.html', context)

def ir_administrar(request):
    pedidos = Pedido.objects.filter()
    usuarios = UsuarioPersonalizado.objects.filter()
    return render(request, 'administrar.html', {'pedidos':pedidos, 'usuarios':usuarios})

@require_POST
def completar_pedido(request, id_pedido):
    try:
        pedido = Pedido.objects.get(id=id_pedido)
        pedido.estado = 'completado'
    except Pedido.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Pedido no encontrado'}, status=404)
    
    carrito = obtener_o_crear_carrito(request)
    carrito.estado = 'pagado'
    carrito.save()
    pedido.save()
    return JsonResponse({'succes':True})

@require_POST
def actualizar_tipo_entrega(request):
    try:
        carrito = obtener_o_crear_carrito(request)
        
        data = json.loads(request.body)
        tipo_entrega = data.get('tipo_entrega')
        direccion = data.get('direccion', '')
        
        if tipo_entrega not in ['retiro', 'delivery']:
            return JsonResponse({'success': False, 'error': 'Tipo de entrega inválido'}, status=400)
        
        carrito.tipo_entrega = tipo_entrega
        
        if tipo_entrega == 'delivery':
            carrito.delivery = 2000
            carrito.direccion = direccion
        else:
            carrito.delivery = 0
            carrito.direccion = None
        
        carrito.save()

        return JsonResponse({
            'success': True,
            'tipo_entrega': carrito.tipo_entrega,
            'delivery': float(carrito.delivery),
            'direccion': carrito.direccion,
            'total': float(carrito.total),
            'descuento': float(carrito.descuento),
            'subtotal': float(carrito.subtotal)
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    detalles = pedido.detalles.all()
    
    context = {
        'pedido': pedido,
        'detalles': detalles,
    }
    return render(request, 'detalle_pedido.html', context)