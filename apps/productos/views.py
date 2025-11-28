from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from apps.productos.models import Producto, Categoria
from apps.ordenes.models import Carrito, ItemCarrito
import json
from django.core.paginator import Paginator

# Create your views here.
def obtener_o_crear_carrito(request):
    """
    Obtiene o crea un carrito para el usuario/sesión actual.
    Evita usar get_or_create para no disparar MultipleObjectsReturned
    y limpia duplicados si los hay.
    """

    # Aseguramos que exista session_key SIEMPRE
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    # ------------------------
    # Usuario autenticado
    # ------------------------
    if request.user.is_authenticated:
        # ✅ CAMBIO: Agregar filtro activo=True
        qs = Carrito.objects.filter(
            usuario=request.user, 
            activo=True,
            pagado=False
        ).order_by('-id')
        carrito = qs.first()

        # Si hay más de uno, dejamos el más nuevo y borramos el resto
        if qs.count() > 1:
            Carrito.objects.filter(
                usuario=request.user,
                activo=True,
                pagado=False
            ).exclude(id=carrito.id).delete()

        # Si ya existe uno, lo usamos
        if carrito:
            if not carrito.session_key:
                carrito.session_key = session_key
                carrito.save(update_fields=['session_key'])
            return carrito

        # Si no existe ninguno, creamos uno nuevo
        return Carrito.objects.create(
            usuario=request.user, 
            session_key=session_key,
            activo=True
        )

    # ------------------------
    # Usuario NO autenticado
    # ------------------------
    # ✅ CAMBIO: Agregar filtro activo=True
    qs = Carrito.objects.filter(
        session_key=session_key,
        usuario__isnull=True,
        activo=True,
        pagado=False
    ).order_by('-id')

    carrito = qs.first()

    # Limpiamos duplicados de sesión (anónimos)
    if qs.count() > 1:
        Carrito.objects.filter(
            session_key=session_key,
            usuario__isnull=True,
            activo=True,
            pagado=False
        ).exclude(id=carrito.id).delete()

    if carrito:
        return carrito

    # Si no hay carrito anónimo, creamos uno
    return Carrito.objects.create(
        session_key=session_key,
        activo=True
    )


def ir_inicio(request):
    productos = Producto.objects.filter(disponible=True)
    categorias = Categoria.objects.filter(activo=True)
    
    categoria_slug = request.GET.get('categoria')
    if categoria_slug:
        productos = productos.filter(categoria__slug=categoria_slug)

    paginador = Paginator(productos, 12)
    pagina_actual = request.GET.get('pagina')
    pagina = paginador.get_page(pagina_actual)
    
    carrito = obtener_o_crear_carrito(request)
    total_items = carrito.total_items
    
    context = {
        'productos': pagina,
        'categorias': categorias,
        'total_items_carrito': total_items,
        'pagina':pagina,
        'subtotal': float(carrito.subtotal)
    }
    return render(request, "index.html", context)


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
    
    print(f"Carrito ID: {carrito.id}")
    print(f"Items: {items.count()}")
    print(f"Subtotal calculado: {carrito.subtotal}")
    print(f"Total calculado: {carrito.total}")

    return JsonResponse({
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
        'total': float(carrito.total),
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
            'item_total': float(item.total),
            'subtotal': float(carrito.subtotal),
            'total': float(carrito.total),
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

        carrito_id = carrito.id
        item.delete()
        
        carrito = Carrito.objects.get(id=carrito_id)
        
        if carrito.total_items == 0:
            carrito.delivery = 0
            carrito.tipo_entrega = 'retiro'
            carrito.activo = False
            carrito.save(update_fields=['delivery', 'tipo_entrega', 'activo'])
        
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
    
###
#CRUD PRODUCTOS
###
def ir_crud_productos(request):
    return render(request, "crud_productos.html")