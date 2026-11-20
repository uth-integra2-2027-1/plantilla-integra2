"""Módulo QR · responsable: (tu nombre). Sólo depende del núcleo."""
import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from nucleo.models import EventoDispositivo, elemento_por_texto, registrar_evento


@login_required
def escanear(request):
    return render(request, "mod_qr/escanear.html", {"recientes": EventoDispositivo.objects.filter(tipo="qr")[:15]})


@login_required
@require_POST
def api_qr(request):
    d = json.loads(request.body or b"{}")
    dato = str(d.get("dato", ""))[:250]
    if not dato:
        return JsonResponse({"ok": False, "error": "lectura vacía"}, status=400)
    elemento = elemento_por_texto(dato)
    registrar_evento("qr", request, dato=dato, elemento=elemento, origen=str(d.get("origen", ""))[:20],
                     duracion_ms=d.get("duracion_ms") or None)
    return JsonResponse({"ok": True, "elemento": str(elemento) if elemento else None})
