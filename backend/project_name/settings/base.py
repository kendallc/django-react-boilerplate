import os

from decouple import config
from dj_database_url import parse as db_url


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def base_dir_join(*args):
    return os.path.join(BASE_DIR, *args)


SITE_ID = 1

DEBUG = True

ADMINS = (("Admin", "foo@example.com"),)

AUTH_USER_MODEL = "users.User"

ALLOWED_HOSTS = []

DATABASES = {
    "default": config("DATABASE_URL", cast=db_url),
}

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_js_reverse",
    "vite_loader",
    "import_export",
    "rest_framework",
    "drf_spectacular",
    "defender",
    "django_guid",
    "common",
    "users",
]

MIDDLEWARE = [
    "django.middleware.gzip.GZipMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django_permissions_policy.PermissionsPolicyMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
    "defender.middleware.FailedLoginMiddleware",
    "django_guid.middleware.guid_middleware",
]

ROOT_URLCONF = "{{ project_name }}.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [base_dir_join("templates")],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "common.context_processors.sentry_dsn",
                "common.context_processors.commit_sha",
            ],
            "loaders": [
                (
                    "django.template.loaders.cached.Loader",
                    [
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ],
                ),
            ],
        },
    },
]

WSGI_APPLICATION = "{{ project_name }}.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# drf-spectacular
SPECTACULAR_SETTINGS = {
    "TITLE": "Vinta Boilerplate API",
    "DESCRIPTION": "A Django project boilerplate with Vinta's best practices",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True


USE_TZ = True

STATICFILES_DIRS = (base_dir_join("../frontend"),)

# Webpack
# Vite configuration
VITE_DEV_MODE = DEBUG
VITE_STATS_FILE = base_dir_join("../webpack-stats.json")  # Keep same filename for compatibility

# Celery
# Recommended settings for reliability: https://gist.github.com/fjsj/da41321ac96cf28a96235cb20e7236f6
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_ACKS_LATE = True
CELERY_TIMEZONE = TIME_ZONE
CELERY_BROKER_TRANSPORT_OPTIONS = {"confirm_publish": True, "confirm_timeout": 5.0}
CELERY_BROKER_POOL_LIMIT = config("CELERY_BROKER_POOL_LIMIT", cast=int, default=1)
CELERY_BROKER_CONNECTION_TIMEOUT = config(
    "CELERY_BROKER_CONNECTION_TIMEOUT", cast=float, default=30.0
)
CELERY_REDIS_MAX_CONNECTIONS = config(
    "CELERY_REDIS_MAX_CONNECTIONS", cast=lambda v: int(v) if v else None, default=None
)
CELERY_TASK_ACKS_ON_FAILURE_OR_TIMEOUT = config(
    "CELERY_TASK_ACKS_ON_FAILURE_OR_TIMEOUT", cast=bool, default=True
)
CELERY_TASK_REJECT_ON_WORKER_LOST = config(
    "CELERY_TASK_REJECT_ON_WORKER_LOST", cast=bool, default=False
)
CELERY_WORKER_PREFETCH_MULTIPLIER = config("CELERY_WORKER_PREFETCH_MULTIPLIER", cast=int, default=1)
CELERY_WORKER_CONCURRENCY = config(
    "CELERY_WORKER_CONCURRENCY", cast=lambda v: int(v) if v else None, default=None
)
CELERY_WORKER_MAX_TASKS_PER_CHILD = config(
    "CELERY_WORKER_MAX_TASKS_PER_CHILD", cast=int, default=1000
)
CELERY_WORKER_SEND_TASK_EVENTS = config("CELERY_WORKER_SEND_TASK_EVENTS", cast=bool, default=True)
CELERY_EVENT_QUEUE_EXPIRES = config("CELERY_EVENT_QUEUE_EXPIRES", cast=float, default=60.0)
CELERY_EVENT_QUEUE_TTL = config("CELERY_EVENT_QUEUE_TTL", cast=float, default=5.0)

# Sentry
SENTRY_DSN = config("SENTRY_DSN", default="")
COMMIT_SHA = config("RENDER_GIT_COMMIT", default="")

# Fix for Safari 12 compatibility issues, please check:
# https://github.com/vintasoftware/safari-samesite-cookie-issue
CSRF_COOKIE_SAMESITE = None
SESSION_COOKIE_SAMESITE = None

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# All available policies are listed at:
# https://github.com/w3c/webappsec-permissions-policy/blob/main/features.md
# Empty list means the policy is disabled
PERMISSIONS_POLICY = {
    "accelerometer": [],
    "camera": [],
    "display-capture": [],
    "encrypted-media": [],
    "geolocation": [],
    "gyroscope": [],
    "magnetometer": [],
    "microphone": [],
    "midi": [],
    "payment": [],
    "usb": [],
    "xr-spatial-tracking": [],
}

# Django-CSP
CSP_INCLUDE_NONCE_IN = ["script-src", "style-src", "font-src"]
CSP_SCRIPT_SRC = (
    [
        "'self'",
        "'unsafe-inline'",
        "'unsafe-eval'",
        "https://browser.sentry-cdn.com",
        # drf-spectacular UI (Swagger and ReDoc)
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/",
        "https://cdn.jsdelivr.net/npm/redoc@latest/",
        "blob:",
    ]
    + (
        [
            # Vite dev server
            "http://localhost:3000",
        ]
        if DEBUG
        else []
    )
    + [f"*{host}" if host.startswith(".") else host for host in ALLOWED_HOSTS]
)
CSP_CONNECT_SRC = (
    [
        "'self'",
        "*.sentry.io",
    ]
    + (
        [
            # Vite dev server
            "http://localhost:3000",
            "ws://localhost:3000",  # For HMR websocket
        ]
        if DEBUG
        else []
    )
    + [f"*{host}" if host.startswith(".") else host for host in ALLOWED_HOSTS]
)
CSP_STYLE_SRC = [
    "'self'",
    "'unsafe-inline'",
    # drf-spectacular UI (Swagger and ReDoc)
    "https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/",
    "https://cdn.jsdelivr.net/npm/redoc@latest/",
    "https://fonts.googleapis.com",
]
CSP_FONT_SRC = [
    "'self'",
    "'unsafe-inline'",
    # drf-spectacular UI (Swagger and ReDoc)
    "https://fonts.gstatic.com",
] + [f"*{host}" if host.startswith(".") else host for host in ALLOWED_HOSTS]
CSP_IMG_SRC = [
    "'self'",
    # drf-spectacular UI (Swagger and ReDoc)
    "data:",
    "https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/",
    "https://cdn.redoc.ly/redoc/",
]

# Django-defender
DEFENDER_LOGIN_FAILURE_LIMIT = 3
DEFENDER_COOLOFF_TIME = 300  # 5 minutes
DEFENDER_LOCKOUT_TEMPLATE = "defender/lockout.html"
DEFENDER_REDIS_URL = config("REDIS_URL")
