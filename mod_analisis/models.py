from django.db import models


class Respuesta(models.Model):
    """Instrumento de ejemplo (Likert 1–5). CÁMBIALO por tu instrumento."""
    consentimiento = models.BooleanField()
    perfil = models.CharField(max_length=60, blank=True)
    facilidad = models.PositiveSmallIntegerField()
    rapidez = models.PositiveSmallIntegerField()
    comentario = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)
