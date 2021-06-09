import os


DEBUG = True

BASE_DIR = os.path.dirname(__file__)

# NOTE: We're using Geospatial sqlite jazz
DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.spatialite",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

SECRET_KEY = "_"

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)


INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "django.contrib.gis",

    "chit_chat",

    "testapp",
)

STATIC_URL = "/static/"

ROOT_URLCONF = "urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True
    }
]
