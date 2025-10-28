from django.contrib import admin
from .models import Carrito, ItemCarrito

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