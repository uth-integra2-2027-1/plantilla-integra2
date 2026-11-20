from django.urls import path

from . import views

urlpatterns = [
    path("encuesta/", views.encuesta, name="encuesta"),
    path("tablero/", views.tablero, name="tablero"),
    path("tablero.json", views.api_tablero, name="api_tablero"),
    path("datos.csv", views.exportar, name="exportar"),
]
