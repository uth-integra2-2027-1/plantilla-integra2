"""Prueba de integración: los cuatro módulos funcionan sobre el núcleo (no la borres)."""
import io

from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from nucleo.models import Elemento, EventoDispositivo


@override_settings(INTEGRA2_EQUIPO="PRUEBA", INTEGRA2_CLAVE="clave-de-prueba")
class IntegracionTests(TestCase):
    def setUp(self):
        User.objects.create_user("op", password="clave-larga-123")
        self.client.login(username="op", password="clave-larga-123")
        self.e = Elemento.objects.create(nombre="Multímetro")

    def test_flujo_completo(self):
        # Impresión: etiqueta firmada
        pagina = self.client.get(f"/impresion/etiqueta/{self.e.folio}/")
        self.assertContains(pagina, self.e.folio)
        texto = pagina.context["texto"]
        self.assertTrue(texto.startswith(f"I2|PRUEBA|{self.e.folio}|"))
        self.assertTrue(self.client.post("/impresion/api/", {"dato": texto}, content_type="application/json").json()["ok"])
        # QR: lectura de la etiqueta
        r = self.client.post("/qr/api/", {"dato": texto, "duracion_ms": 900, "origen": "usb"}, content_type="application/json").json()
        self.assertIn(self.e.folio, r["elemento"])
        # Cámara: foto ligada al folio
        foto = io.BytesIO(b"\xff\xd8\xff\xe0" + b"0" * 2000)
        foto.name = "foto.jpg"
        self.assertTrue(self.client.post("/camara/api/", {"foto": foto, "folio": self.e.folio, "ancho": 1280, "alto": 720}).json()["ok"])
        # Análisis: encuesta pública y tablero
        self.client.logout()
        self.client.post("/analisis/encuesta/", {"consentimiento": "on", "perfil": "alumno", "facilidad": 5, "rapidez": 4})
        self.assertEqual(set(EventoDispositivo.objects.values_list("tipo", flat=True)), {"qr", "foto", "impresion", "encuesta"})
        d = self.client.get("/analisis/tablero.json").json()
        self.assertEqual(d["encuesta"]["n"], 1)
        estado = self.client.get("/integra2/estado.json?reto=x").json()
        self.assertEqual(set(estado["dispositivos"]), {"qr", "foto", "impresion", "encuesta"})
        for url in ["/qr/", "/camara/", "/analisis/tablero/", "/elementos/", "/integra2/checkin/"]:
            self.assertEqual(self.client.get(url).status_code, 302, url)  # requieren iniciar sesión
