"""Módulo Análisis · responsable: (tu nombre). Sólo depende del núcleo."""
import csv
from collections import defaultdict

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.db.models.functions import TruncDate
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from nucleo.models import EventoDispositivo, registrar_evento

from .models import Respuesta

ESCALA = [(i, str(i)) for i in range(1, 6)]


class RespuestaForm(forms.ModelForm):
    facilidad = forms.TypedChoiceField(choices=ESCALA, coerce=int, widget=forms.RadioSelect, label="¿Qué tan fácil fue registrarse?")
    rapidez = forms.TypedChoiceField(choices=ESCALA, coerce=int, widget=forms.RadioSelect, label="¿Qué tan rápido fue el registro?")

    class Meta:
        model = Respuesta
        fields = ["consentimiento", "perfil", "facilidad", "rapidez", "comentario"]
        labels = {"consentimiento": "Acepto participar y conozco el aviso de privacidad"}

    def clean_consentimiento(self):
        if not self.cleaned_data["consentimiento"]:
            raise forms.ValidationError("Se requiere tu consentimiento para participar.")
        return True


def encuesta(request):
    form = RespuestaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        r = form.save()
        registrar_evento("encuesta", request, dato=f"respuesta:{r.pk}", origen="web")
        messages.success(request, "¡Gracias por participar!")
        return redirect("encuesta")
    return render(request, "mod_analisis/encuesta.html", {"form": form})


@login_required
def tablero(request):
    return render(request, "mod_analisis/tablero.html")


def api_tablero(request):
    por_dia = defaultdict(lambda: {"qr": 0, "foto": 0, "impresion": 0, "encuesta": 0})
    for r in EventoDispositivo.objects.annotate(dia=TruncDate("creado")).values("dia", "tipo").annotate(n=Count("id")):
        por_dia[r["dia"].isoformat()][r["tipo"]] = r["n"]
    dias = sorted(por_dia)
    enc = Respuesta.objects.aggregate(facilidad=Avg("facilidad"), rapidez=Avg("rapidez"), n=Count("id"))
    tiempo = EventoDispositivo.objects.filter(tipo="qr", duracion_ms__isnull=False).aggregate(prom=Avg("duracion_ms"), n=Count("id"))
    return JsonResponse({"dias": dias, "series": {t: [por_dia[d][t] for d in dias] for t in ("qr", "foto", "impresion")},
                         "encuesta": enc, "tiempo_qr_ms": tiempo})


@login_required
def exportar(request):
    """Datos anonimizados para data/u3/datos_anonimizados.csv"""
    resp = HttpResponse(content_type="text/csv; charset=utf-8")
    resp["Content-Disposition"] = 'attachment; filename="datos_anonimizados.csv"'
    w = csv.writer(resp)
    w.writerow(["fuente", "id", "fecha", "tipo_o_perfil", "duracion_ms", "facilidad", "rapidez"])
    for e in EventoDispositivo.objects.order_by("creado"):
        w.writerow(["evento", e.pk, timezone.localtime(e.creado).isoformat(), e.tipo, e.duracion_ms or "", "", ""])
    for r in Respuesta.objects.order_by("creado"):
        w.writerow(["encuesta", r.pk, timezone.localtime(r.creado).isoformat(), r.perfil, "", r.facilidad, r.rapidez])
    return resp
