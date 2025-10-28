from django.db import models

from django.contrib.auth.models import User
from apps.productos.models import Producto

class Carrito(models.Model):
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Carrito'
        verbose_name_plural = 'Carritos'
    
    def __str__(self):
        if self.usuario:
            return f"Carrito de {self.usuario.username}"
        return f"Carrito {self.session_key}"
    
    @property
    def total_items(self):
        return sum(item.cantidad for item in self.items.all())
    
    @property
    def subtotal(self):
        return sum(item.total for item in self.items.all())
    
    @property
    def total(self):
        return self.subtotal


class ItemCarrito(models.Model):
    carrito = models.ForeignKey(
        Carrito, 
        on_delete=models.CASCADE, 
        related_name='items'
    )
    producto = models.ForeignKey(
        Producto, 
        on_delete=models.CASCADE
    )
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