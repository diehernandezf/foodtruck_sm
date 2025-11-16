from django.contrib import admin
from .models import Carrito, ItemCarrito, Pedido, DetallePedido

class ItemCarritoInline(admin.TabularInline):
    model = ItemCarrito
    extra = 0

@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'session_key', 'total_items', 'total', 'creado']
    inlines = [ItemCarritoInline]

@admin.register(ItemCarrito)
class ItemCarritoAdmin(admin.ModelAdmin):
    list_display = ['carrito', 'producto', 'cantidad', 'precio_unitario', 'total']

class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = ('producto', 'nombre_producto', 'cantidad', 'precio_unitario', 'subtotal')
    can_delete = False

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'total', 'estado', 'fecha')
    list_filter = ('estado', 'fecha')
    search_fields = ('usuario__username', 'orden_compra', 'codigo_autorizacion')
    readonly_fields = ('fecha', 'fecha', 'token', 'codigo_autorizacion', 'orden_compra')
    inlines = [DetallePedidoInline]
    
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('usuario', 'total', 'estado')
        }),
        ('Información de Pago', {
            'fields': ('token', 'codigo_autorizacion', 'orden_compra')
        }),
        ('Fechas', {
            'fields': ('fecha',)
        }),
    )