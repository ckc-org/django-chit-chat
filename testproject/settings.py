import os


DEBUG = True

BASE_DIR = os.path.dirname(__file__)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        # "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
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

    "chit_chat",

    "testapp",
    'channels',
)

AUTH_USER_MODEL = 'testapp.User'

STATIC_URL = "/static/"

ROOT_URLCONF = "urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True
    }
]

# =============================================================================
# DRF
# =============================================================================
REST_FRAMEWORK = {
    # 'DEFAULT_AUTHENTICATION_CLASSES': (
    #     'rest_framework.authentication.TokenAuthentication',
    #     'rest_framework.authentication.SessionAuthentication',
    #     'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
    # ),
    # 'DEFAULT_PERMISSION_CLASSES': (
    #     'rest_framework.permissions.IsAuthenticated',
    # ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,
    # 'DATETIME_INPUT_FORMATS': (
    #     'iso-8601',
    #     '%B %d, %Y',
    # )
}


# =============================================================================
# Channels
# =============================================================================
ASGI_APPLICATION = "routing.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    },
}
