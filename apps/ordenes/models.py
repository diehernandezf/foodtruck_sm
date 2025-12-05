from decimal import Decimal
from django.db import models

from django.conf import settings
from apps.productos.models import Producto

from django.db.models import Q


class Carrito(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('cancelado', 'Cancelado'),
        ('completado', 'Completado'),
    ]
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    token = models.CharField(max_length=200, null=True, blank=True, unique=True)
    pagado = models.BooleanField(default=False)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    activo = models.BooleanField(default=True)
    delivery = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tipo_entrega = models.CharField(max_length=40, null=True, blank=True, choices=[('retiro', 'Retiro'), ('delivery', 'Delivery')], default='retiro')
    direccion = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Carrito'
        verbose_name_plural = 'Carritos'
        constraints = [
            # Solo un carrito activo no pagado por usuario
            models.UniqueConstraint(
                fields=['usuario'],
                condition=Q(activo=True, pagado=False, usuario__isnull=False),
                name='uniq_active_cart_per_user'
            ),
            # Solo un carrito activo no pagado por session anónima
            models.UniqueConstraint(
                fields=['session_key'],
                condition=Q(activo=True, pagado=False, usuario__isnull=True),
                name='uniq_active_cart_per_session'
            ),
        ]
    
    def __str__(self):
        if self.usuario:
            return f"Carrito de {self.usuario.username}"
        return f"Carrito {self.session_key}"
    
    @property
    def total_items(self):
        return sum(item.cantidad for item in self.items.all())
    
    @property
    def subtotal(self):
        return sum(item.total for item in self.items.all())# entender de donde viene el self.items
    
    @property
    def descuento(self):
        try:
            subtotal = self.subtotal
            if not subtotal or subtotal == 0:
                return Decimal('0')
            total_pedidos = getattr(self.usuario, 'total_pedidos', 0) if self.usuario else 0
            if total_pedidos == 0:
                return subtotal * Decimal('0.30')
            elif (total_pedidos + 1) % 3 == 0:
                return subtotal * Decimal('0.25')
            else:
                return Decimal('0')
        except:
            return Decimal('0')
    
    @property
    def total(self):
        delivery = self.delivery or Decimal('0')
        return (self.subtotal - self.descuento) + delivery


class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Item del Carrito'
        verbose_name_plural = 'Items del Carrito'
        unique_together = ['carrito', 'producto']
    
    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"
    
    @property
    def total(self):
        return self.cantidad * self.precio_unitario
    
    def save(self, *args, **kwargs):
        if not self.precio_unitario:
            self.precio_unitario = self.producto.precio
        super().save(*args, **kwargs)

class Pedido(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('cancelado', 'Cancelado'),
        ('completado', 'Completado'),
    ]
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='pedidos')
    token = models.CharField(max_length=100)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    fecha = models.DateTimeField(auto_now_add=True)
    delivery = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tipo_entrega = models.CharField(max_length=40, null=True, blank=True)
    direccion = models.CharField(max_length=100, null=True, blank=True)

    codigo_autorizacion = models.CharField(max_length=100, blank=True, null=True)
    orden_compra = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
    
    def __str__(self):
        if self.usuario:
            return f"Pedido #{self.id} - {self.usuario.username}"
        else:
            return f"Pedido #{self.id} - Anónimo"
    
class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    nombre_producto = models.CharField(max_length=200)  # Guardamos el nombre por si se borra el producto
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = 'Detalle de Pedido'
        verbose_name_plural = 'Detalles de Pedidos'
    
    def __str__(self):
        return f"{self.cantidad}x {self.nombre_producto}"
    
    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)