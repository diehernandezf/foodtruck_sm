from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class UsuarioPersonalizado(AbstractUser):
    telefono = models.CharField("Telefono", max_length=15, null=True)

    @property # convierte un metodo en un atributo, osea es legible como atributo, pero ejecuta codigo
    def total_pedidos(self):
        return self.pedidos.filter(estado__in=['pagado', 'completado']).count() # No funciona