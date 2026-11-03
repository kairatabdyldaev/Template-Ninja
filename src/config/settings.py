import tomllib
from pathlib import Path
from typing import Any

from django.core.exceptions import ImproperlyConfigured
from pydantic import BaseModel, ConfigDict, ValidationError

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = BASE_DIR / "config.toml"


class DatabaseConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    engine: str = "django.db.backends.postgresql"
    name: str
    user: str
    password: str = ""
    host: str = "127.0.0.1"
    port: int = 5432
    conn_max_age: int = 60

    def as_django(self) -> dict[str, Any]:
        return {
            "ENGINE": self.engine,
            "NAME": self.name,
            "USER": self.user,
            "PASSWORD": self.password,
            "HOST": self.host,
            "PORT": self.port,
            "CONN_MAX_AGE": self.conn_max_age,
        }


class MailConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    backend: str = "django.core.mail.backends.console.EmailBackend"


class FileConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    debug: bool = False
    secret_key: str
    allowed_hosts: list[str]
    time_zone: str = "Asia/Bishkek"
    database: DatabaseConfig
    mail: MailConfig = MailConfig()


def load_config(path: Path = CONFIG_PATH) -> FileConfig:
    if not path.is_file():
        raise ImproperlyConfigured(f"Config file not found: {path}")
    with path.open("rb") as config_file:
        raw = tomllib.load(config_file)
    try:
        return FileConfig.model_validate(raw)
    except ValidationError as exc:
        raise ImproperlyConfigured(f"{path.name} is invalid: {exc}") from exc


_config = load_config()

SECRET_KEY = _config.secret_key
DEBUG = _config.debug
ALLOWED_HOSTS = _config.allowed_hosts
TIME_ZONE = _config.time_zone
DATABASES = {"default": _config.database.as_django()}
MAILERS = {"default": {"BACKEND": _config.mail.backend}}

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "src.core.apps.CoreConfig",
    "src.tasks.apps.TasksConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "src.config.urls"
WSGI_APPLICATION = "src.config.wsgi.application"
ASGI_APPLICATION = "src.config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.BCryptPasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]

LANGUAGE_CODE = "ru"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

HEALTH_CHECKS = {
    "postgresql": "django_healthchecks.contrib.check_database",
}
HEALTH_CHECKS_ERROR_CODE = 503
