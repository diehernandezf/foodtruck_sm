"""
Importar settings según el ambiente
"""
import os

# Por defecto usa development
DJANGO_ENV = os.getenv('DJANGO_ENV', 'development')

if DJANGO_ENV == 'production':
    from .production import *
else:
    from .development import *