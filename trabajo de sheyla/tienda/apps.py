"""
Configuración de la aplicación de tienda para Django.

Este módulo contiene la configuración específica de la aplicación 'tienda',
incluyendo el campo de clave primaria predeterminado y el nombre de la aplicación.
"""
from django.apps import AppConfig


class TiendaConfig(AppConfig):
    """
    Configuración de la aplicación 'tienda'.
    
    Atributos:
        default_auto_field: Define el tipo de campo automático predeterminado para los modelos
        name: Nombre de la aplicación (debe coincidir con el nombre del paquete)
    """
    # Define el tipo de campo automático predeterminado para los modelos
    # Utiliza BigAutoField para soportar claves primarias grandes
    default_auto_field = 'django.db.models.BigAutoField'
    
    # Nombre completo de Python de la aplicación
    name = 'tienda'
