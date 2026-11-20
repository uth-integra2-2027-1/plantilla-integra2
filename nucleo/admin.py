from django.contrib import admin

from .models import Elemento, EventoDispositivo


@admin.register(Elemento)
class ElementoAdmin(admin.ModelAdmin):
    list_display = ("folio", "nombre", "categoria", "creado")
    search_fields = ("folio", "nombre")


@admin.register(EventoDispositivo)
class EventoAdmin(admin.ModelAdmin):
    list_display = ("creado", "tipo", "dato", "elemento", "origen", "duracion_ms", "usuario")
    list_filter = ("tipo", "origen")
