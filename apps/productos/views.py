from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from apps.productos.models import Producto, Categoria
from apps.ordenes.models import Carrito, ItemCarrito
import json

# Create your views here.
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


def ir_inicio(request):
    """Vista principal con productos"""
    productos = Producto.objects.filter(disponible=True)
    categorias = Categoria.objects.filter(activo=True)
    
    categoria_slug = request.GET.get('categoria')
    if categoria_slug:
        productos = productos.filter(categoria__slug=categoria_slug)
    
    carrito = obtener_o_crear_carrito(request)
    total_items = carrito.total_items
    
    context = {
        'productos': productos,
        'categorias': categorias,
        'total_items_carrito': total_items,
    }
    return render(request, "pages/index.html", context)


@require_POST
def agregar_al_carrito(request):
    """Agrega un producto al carrito vía AJAX"""
    try:
        data = json.loads(request.body)
        producto_id = data.get('producto_id')
        cantidad = int(data.get('cantidad', 1))
        
        producto = get_object_or_404(Producto, id=producto_id, disponible=True)
        carrito = obtener_o_crear_carrito(request)
        
        item, created = ItemCarrito.objects.get_or_create(
            carrito=carrito,
            producto=producto,
            defaults={'precio_unitario': producto.precio, 'cantidad': cantidad}
        )
        
        if not created:
            item.cantidad += cantidad
            item.save()
        
        return JsonResponse({
            'success': True,
            'message': f'{producto.nombre} agregado al carrito',
            'total_items': carrito.total_items,
            'subtotal': str(carrito.subtotal)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


def ver_carrito(request):
    """Vista para ver el contenido del carrito"""
    carrito = obtener_o_crear_carrito(request)
    items = carrito.items.select_related('producto').all()
    
    return JsonResponse({
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
    })


@require_POST
def actualizar_cantidad(request):
    """Actualiza la cantidad de un item en el carrito"""
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        cantidad = int(data.get('cantidad'))
        
        if cantidad < 1:
            return JsonResponse({
                'success': False,
                'message': 'La cantidad debe ser al menos 1'
            }, status=400)
        
        carrito = obtener_o_crear_carrito(request)
        item = get_object_or_404(ItemCarrito, id=item_id, carrito=carrito)
        item.cantidad = cantidad
        item.save()
        
        return JsonResponse({
            'success': True,
            'item_total': str(item.total),
            'subtotal': str(carrito.subtotal),
            'total': str(carrito.total),
            'total_items': carrito.total_items
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@require_POST
def eliminar_del_carrito(request):
    """Elimina un item del carrito"""
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        
        carrito = obtener_o_crear_carrito(request)
        item = get_object_or_404(ItemCarrito, id=item_id, carrito=carrito)
        item.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Producto eliminado del carrito',
            'subtotal': str(carrito.subtotal),
            'total': str(carrito.total),
            'total_items': carrito.total_items
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@require_POST
def vaciar_carrito(request):
    """Vacía el carrito completo"""
    try:
        carrito = obtener_o_crear_carrito(request)
        carrito.items.all().delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Carrito vaciado'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)