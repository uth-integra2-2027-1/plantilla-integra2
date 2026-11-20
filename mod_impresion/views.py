"""Módulo Impresión · responsable: (tu nombre). Sólo depende del núcleo."""
import hashlib
import hmac
import io
import json
import time

import qrcode
import qrcode.image.svg
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from nucleo.models import Elemento, elemento_por_texto, registrar_evento


def qr_svg(texto, escala=8):
    buf = io.BytesIO()
    qrcode.make(texto, image_factory=qrcode.image.svg.SvgPathImage, box_size=escala, border=1).save(buf)
    return buf.getvalue().decode()


def texto_etiqueta(folio):
    """QR firmado que el docente valida con el escáner de Integra2: I2|equipo|folio|epoch|firma16"""
    epoch = str(int(time.time()))
    msg = f"{settings.INTEGRA2_EQUIPO}|{folio}|{epoch}"
    firma = hmac.new(settings.INTEGRA2_CLAVE.encode(), msg.encode(), hashlib.sha256).hexdigest()[:16] \
        if settings.INTEGRA2_CLAVE else "sin-clave"
    return f"I2|{msg}|{firma}"


@login_required
def etiqueta(request, folio):
    e = get_object_or_404(Elemento, folio=folio)
    texto = texto_etiqueta(e.folio)
    return render(request, "mod_impresion/etiqueta.html", {"e": e, "svg": qr_svg(texto), "texto": texto})


@login_required
@require_POST
def api_impresion(request):
    d = json.loads(request.body or b"{}")
    dato = str(d.get("dato", ""))[:250]
    registrar_evento("impresion", request, dato=dato, elemento=elemento_por_texto(dato), origen="navegador")
    return JsonResponse({"ok": True})
