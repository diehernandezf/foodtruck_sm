from django.http import JsonResponse
from django.shortcuts import render

from apps.ordenes.models import Carrito

# Create your views here.

def ir_miPedido(request):
    carrito = obtener_o_crear_carrito(request)
    items = carrito.items.select_related('producto').all()
    
    context = {
        'items': [
            {
                'id': item.id,
                'producto_id': item.producto.id,
                'nombre': item.producto.nombre,
                'precio_unitario': str(item.precio_unitario),
                'cantidad': item.cantidad,
                'total': str(item.total),
                'imagen_url': item.producto.imagen_url
            }
            for item in items
        ],
        'subtotal': str(carrito.subtotal),
        'total': str(carrito.total),
        'total_items': carrito.total_items
    }

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(context)

    return render(request, 'miPedido.html', context)

def obtener_o_crear_carrito(request):
    """Obtiene o crea un carrito para el usuario/sesión actual"""
    if request.user.is_authenticated:
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        carrito, created = Carrito.objects.get_or_create(session_key=session_key)
    return carrito