from sqladmin import Admin as DefaultAdmin

from wacruit.src.settings import settings

from .applications import HttpsAdmin

Admin = DefaultAdmin if settings.is_local or settings.is_test else HttpsAdmin
