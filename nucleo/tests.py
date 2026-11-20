"""Pruebas del núcleo y de la integración con Integra2 (no las borres)."""
import hashlib
import hmac

from django.test import TestCase, override_settings

from .models import Elemento, EventoDispositivo, elemento_por_texto


@override_settings(INTEGRA2_EQUIPO="PRUEBA", INTEGRA2_CLAVE="clave-de-prueba")
class NucleoTests(TestCase):
    def test_estado_json(self):
        EventoDispositivo.objects.create(tipo="qr", dato="x")
        EventoDispositivo.objects.create(tipo="foto", dato="y")
        r = self.client.get("/integra2/estado.json?reto=abc123").json()
        self.assertEqual(r["proyecto"], "integra2")
        self.assertEqual(r["equipo"], "PRUEBA")
        self.assertEqual(r["firma"], hmac.new(b"clave-de-prueba", b"abc123", hashlib.sha256).hexdigest())
        self.assertEqual(sum(r["dispositivos"]["qr"].values()), 1)
        self.assertEqual(sum(r["dispositivos"]["foto"].values()), 1)

    def test_elemento_por_texto(self):
        e = Elemento.objects.create(nombre="Multímetro")
        self.assertEqual(elemento_por_texto(e.folio), e)
        self.assertEqual(elemento_por_texto(f"I2|PRUEBA|{e.folio}|1700000000|abcd"), e)

    def test_paginas_publicas(self):
        for url in ["/", "/aviso-de-privacidad/", "/divulgacion/"]:
            self.assertEqual(self.client.get(url).status_code, 200, url)
        self.assertContains(self.client.get("/divulgacion/"), "integra2-divulgacion")
