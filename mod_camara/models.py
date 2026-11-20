from django.db import models

from nucleo.models import Elemento


class Foto(models.Model):
    """Foto comprimida guardada en TiDB Cloud. AGREGA tus variables."""
    elemento = models.ForeignKey(Elemento, models.SET_NULL, null=True, blank=True)
    imagen = models.BinaryField()
    ancho = models.PositiveIntegerField(default=0)
    alto = models.PositiveIntegerField(default=0)
    creado = models.DateTimeField(auto_now_add=True)
