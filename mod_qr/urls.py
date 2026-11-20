from django.urls import path

from . import views

urlpatterns = [
    path("", views.escanear, name="escanear"),
    path("api/", views.api_qr, name="api_qr"),
]
