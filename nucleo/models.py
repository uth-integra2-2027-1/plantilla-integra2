"""NÚCLEO COMÚN: lo único que comparten los módulos. Cámbialo sólo de acuerdo con todo el equipo."""
import secrets

from django.db import models


def _folio():
    return "F-" + secrets.token_hex(3).upper()


class Elemento(models.Model):
    """Lo que se registra o rastrea: equipo de laboratorio, pedido, participante, paquete…"""
    folio = models.CharField(max_length=20, unique=True, default=_folio)
    nombre = models.CharField(max_length=150)
    categoria = models.CharField(max_length=80, blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado"]

    def __str__(self):
        return f"{self.folio} · {self.nombre}"


class EventoDispositivo(models.Model):
    """Bitácora común de uso de dispositivos. Cada módulo registra los suyos; Integra2 los cuenta por día."""
    TIPOS = [("qr", "Lectura QR"), ("foto", "Foto de cámara"), ("impresion", "Impresión"), ("encuesta", "Respuesta de instrumento")]
    tipo = models.CharField(max_length=10, choices=TIPOS)
    elemento = models.ForeignKey(Elemento, on_delete=models.SET_NULL, null=True, blank=True)
    dato = models.CharField(max_length=250, blank=True)
    origen = models.CharField(max_length=20, blank=True, help_text="usb | camara | navegador | web")
    duracion_ms = models.PositiveIntegerField(null=True, blank=True, help_text="Tiempo de registro (variable de investigación)")
    usuario = models.CharField(max_length=150, blank=True)
    creado = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-creado"]


def registrar_evento(tipo, request=None, **campos):
    """API del núcleo para los módulos: registra un uso de dispositivo."""
    usuario = request.user.get_username() if request is not None and request.user.is_authenticated else ""
    return EventoDispositivo.objects.create(tipo=tipo, usuario=usuario, **campos)


def elemento_por_texto(texto):
    """Encuentra el Elemento a partir de un folio o de un QR de etiqueta I2|equipo|folio|epoch|firma."""
    texto = (texto or "").strip()
    folio = texto.split("|")[2] if texto.startswith("I2|") and texto.count("|") == 4 else texto
    return Elemento.objects.filter(folio=folio).first()
