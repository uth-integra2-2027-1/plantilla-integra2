"""Configuración del proyecto del equipo (Django + TiDB Cloud + Render)."""
import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = os.environ.get("DEBUG", "0") == "1"
SECRET_KEY = os.environ.get("SECRET_KEY") or ("dev-solo-local" if DEBUG else None)
if not SECRET_KEY:
    raise RuntimeError("Define SECRET_KEY en Render (Environment).")

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
if os.environ.get("RENDER_EXTERNAL_HOSTNAME"):
    ALLOWED_HOSTS.append(os.environ["RENDER_EXTERNAL_HOSTNAME"])
CSRF_TRUSTED_ORIGINS = [f"https://{h}" for h in ALLOWED_HOSTS if "." in h and not h[0].isdigit()]

# Integración con Integra2 (datos en tu portal: https://integra2.sistemasprado.mx)
INTEGRA2_URL = os.environ.get("INTEGRA2_URL", "https://integra2.sistemasprado.mx").rstrip("/")
INTEGRA2_EQUIPO = os.environ.get("INTEGRA2_EQUIPO", "")   # código público del equipo
INTEGRA2_CLAVE = os.environ.get("INTEGRA2_CLAVE", "")     # secreto: SÓLO en Render, nunca en GitHub

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "nucleo", "mod_qr", "mod_camara", "mod_impresion", "mod_analisis",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "proyecto.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates", "DIRS": [], "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request", "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages", "nucleo.views.contexto"]},
}]
WSGI_APPLICATION = "proyecto.wsgi.application"

# TiDB Cloud (MySQL) con PyMySQL + SSL. Sin DATABASE_URL usa SQLite (sólo para desarrollo local).
if os.environ.get("DATABASE_URL"):
    import certifi
    import pymysql
    pymysql.install_as_MySQLdb()
    DATABASES = {"default": dj_database_url.parse(os.environ["DATABASE_URL"], conn_max_age=300)}
    DATABASES["default"].setdefault("OPTIONS", {}).update({"ssl": {"ca": certifi.where()}, "charset": "utf8mb4"})
else:
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "local.sqlite3"}}

LANGUAGE_CODE = "es-mx"
TIME_ZONE = "America/Hermosillo"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {"default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
            "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"}}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "/admin/login/"
DATA_UPLOAD_MAX_MEMORY_SIZE = 3 * 1024 * 1024

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
