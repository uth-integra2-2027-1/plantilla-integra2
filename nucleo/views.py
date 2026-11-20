"""Vistas del núcleo: páginas generales, catálogo de elementos e integración con Integra2."""
import hashlib
import hmac
import json
import os
from collections import defaultdict

import requests
from django import forms
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import Elemento, EventoDispositivo, registrar_evento


def contexto(request):
    return {"EQUIPO": settings.INTEGRA2_EQUIPO}


def firmar(mensaje):
    return hmac.new(settings.INTEGRA2_CLAVE.encode(), mensaje.encode(), hashlib.sha256).hexdigest()


def inicio(request):
    return render(request, "nucleo/inicio.html")


def aviso(request):
    return render(request, "nucleo/aviso.html")


def divulgacion(request):
    return render(request, "nucleo/divulgacion.html")


class ElementoForm(forms.ModelForm):
    class Meta:
        model = Elemento
        fields = ["nombre", "categoria"]


@login_required
def elementos(request):
    form = ElementoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("elementos")
    return render(request, "nucleo/elementos.html", {"form": form, "elementos": Elemento.objects.all()[:200]})


# --------------------------------------------------------------------------- Integra2 (NO MODIFICAR)
def estado_integra2(request):
    reto = request.GET.get("reto", "")[:64]
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT VERSION()")
            version = cur.fetchone()[0]
    except Exception as ex:
        version = f"error: {ex.__class__.__name__}"
    dispositivos = defaultdict(dict)
    for r in EventoDispositivo.objects.annotate(dia=TruncDate("creado")).values("dia", "tipo").annotate(n=Count("id")):
        dispositivos[r["tipo"]][r["dia"].isoformat()] = r["n"]
    return JsonResponse({
        "proyecto": "integra2",
        "equipo": settings.INTEGRA2_EQUIPO,
        "commit": os.environ.get("RENDER_GIT_COMMIT", ""),
        "bd": {"motor": connection.vendor, "version": version},
        "reto": reto,
        "firma": firmar(reto) if settings.INTEGRA2_CLAVE and reto else "",
        "dispositivos": dispositivos,
        "generado": timezone.now().isoformat(),
    })


@login_required
def checkin(request):
    """Escanea el QR del proyector del docente y lo reenvía firmado a Integra2."""
    if request.method == "POST":
        d = json.loads(request.body or b"{}")
        token, matricula = str(d.get("token", "")), str(d.get("matricula", "")).strip()
        cuerpo = {"equipo": settings.INTEGRA2_EQUIPO, "matricula": matricula, "token": token,
                  "firma": firmar(f"{token}|{matricula}")}
        try:
            r = requests.post(f"{settings.INTEGRA2_URL}/api/checkin/", json=cuerpo, timeout=60)
            registrar_evento("qr", request, dato="checkin", origen=str(d.get("origen", ""))[:20])
            return JsonResponse(r.json(), status=r.status_code)
        except (requests.RequestException, ValueError) as ex:
            return JsonResponse({"ok": False, "error": f"Integra2 no respondió: {ex.__class__.__name__}"}, status=502)
    return render(request, "nucleo/checkin.html")
