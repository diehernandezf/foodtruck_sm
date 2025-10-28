"""
Configuración para ambiente de producción
"""
from .base import *

DEBUG = False

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Transbank en producción
TRANSBANK_ENVIRONMENT = 'production'
TRANSBANK_COMMERCE_CODE = env('TRANSBANK_COMMERCE_CODE')
TRANSBANK_API_KEY = env('TRANSBANK_API_KEY')