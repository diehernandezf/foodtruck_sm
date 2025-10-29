from django.db import models

from django.core.validators import MinValueValidator
from decimal import Decimal

# Create your models here.

class Transaccion(models.Model):
    orden_compra = models.CharField(max_length=100)
    id_sesion = models.CharField(max_length=100)
    monto = models.DecimalField(
            max_digits=10, 
            decimal_places=2,
            validators=[MinValueValidator(Decimal('0.01'))]
        )
    status = models.CharField(max_length=100)
    token = models.CharField(max_length=100)
    fecha_transaccion = models.DateTimeField(auto_now_add=True)