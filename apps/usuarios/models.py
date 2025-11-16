from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class UsuarioPersonalizado(AbstractUser):
    telefono = models.CharField("Telefono", max_length=15, blank=True, null=True)

    @property # convierte un metodo en un atributo, osea es legible como atributo, pero ejecuta codigo
    def total_pedidos(self):
        # Se cuenta los carritos pagados del usuario
        return self.carrito_set.filter(pagado=True).count() # carrito_set accede a los carrito del usuario