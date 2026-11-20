from django.contrib import admin
from django.urls import include, path

from nucleo import views as nucleo

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", nucleo.inicio, name="inicio"),
    path("aviso-de-privacidad/", nucleo.aviso, name="aviso"),
    path("divulgacion/", nucleo.divulgacion, name="divulgacion"),
    path("elementos/", nucleo.elementos, name="elementos"),
    # Integración con Integra2 (no cambiar estas rutas)
    path("integra2/estado.json", nucleo.estado_integra2, name="estado_integra2"),
    path("integra2/checkin/", nucleo.checkin, name="checkin"),
    # Módulos independientes (uno por integrante)
    path("qr/", include("mod_qr.urls")),
    path("camara/", include("mod_camara.urls")),
    path("impresion/", include("mod_impresion.urls")),
    path("analisis/", include("mod_analisis.urls")),
]
