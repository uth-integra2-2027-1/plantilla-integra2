"""Módulo Cámara · responsable: (tu nombre). Sólo depende del núcleo."""
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from nucleo.models import elemento_por_texto, registrar_evento

from .models import Foto


@login_required
def camara(request):
    return render(request, "mod_camara/camara.html", {"fotos": Foto.objects.order_by("-creado").defer("imagen")[:12]})


@login_required
def foto(request, pk):
    return HttpResponse(bytes(get_object_or_404(Foto, pk=pk).imagen), content_type="image/jpeg")


@login_required
@require_POST
def api_foto(request):
    archivo = request.FILES.get("foto")
    if not archivo or archivo.size > 1_500_000:
        return JsonResponse({"ok": False, "error": "foto ausente o mayor a 1.5 MB"}, status=400)
    elemento = elemento_por_texto(request.POST.get("folio", ""))
    f = Foto.objects.create(elemento=elemento, imagen=archivo.read(),
                            ancho=int(request.POST.get("ancho") or 0), alto=int(request.POST.get("alto") or 0))
    registrar_evento("foto", request, elemento=elemento, dato=f"foto:{f.pk}", origen="camara")
    return JsonResponse({"ok": True, "id": f.pk})
