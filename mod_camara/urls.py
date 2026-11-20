from django.urls import path

from . import views

urlpatterns = [
    path("", views.camara, name="camara"),
    path("foto/<int:pk>/", views.foto, name="foto"),
    path("api/", views.api_foto, name="api_foto"),
]
