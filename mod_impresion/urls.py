from django.urls import path

from . import views

urlpatterns = [
    path("etiqueta/<str:folio>/", views.etiqueta, name="etiqueta"),
    path("api/", views.api_impresion, name="api_impresion"),
]
