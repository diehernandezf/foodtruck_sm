"""
Configuración para ambiente de desarrollo
"""
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Email en consola para desarrollo
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Transbank en modo integración
TRANSBANK_ENVIRONMENT = 'integration'
TRANSBANK_COMMERCE_CODE = '597055555532'
TRANSBANK_API_KEY = '579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C'