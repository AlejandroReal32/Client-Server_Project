#!/usr/bin/env python
"""
manage.py

Este archivo es la utilidad de línea de comandos para tareas administrativas de Django.
Permite ejecutar comandos como iniciar el servidor, migraciones, crear superusuarios, etc.

Uso:
    python manage.py <comando>
"""

import os
import sys


def main():
    """
    Ejecuta tareas administrativas de Django.

    - Establece la variable de entorno DJANGO_SETTINGS_MODULE.
    - Intenta importar y ejecutar 'execute_from_command_line' de Django.
    - Si Django no está instalado, lanza un error informativo.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pcstore.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    # Punto de entrada principal del script.
    main()
