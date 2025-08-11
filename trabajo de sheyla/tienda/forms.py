"""
Formularios para la aplicación de tienda.

Este módulo contiene las definiciones de los formularios utilizados para la interacción
con los modelos de la aplicación, incluyendo el registro de usuarios, gestión de
productos y categorías.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Producto, Categoria

class RegistroUsuarioForm(UserCreationForm):
    """
    Formulario personalizado para el registro de nuevos usuarios.
    
    Extiende UserCreationForm para incluir el campo de email como obligatorio.
    """
    email = forms.EmailField(required=True, help_text="Correo electrónico obligatorio")
    
    class Meta:
        """
        Configuración del formulario de registro.
        
        Atributos:
            model: Modelo de usuario de Django
            fields: Campos a incluir en el formulario
        """
        model = User
        fields = ["username", "email", "password1", "password2"]

class ProductoForm(forms.ModelForm):
    """
    Formulario para crear y editar productos.
    
    Incluye todos los campos del modelo Producto con widgets personalizados
    para mejorar la experiencia de usuario.
    """
    class Meta:
        """
        Configuración del formulario de productos.
        
        Atributos:
            model: Modelo Producto
            fields: Lista de campos a incluir en el formulario
            widgets: Personalización de los widgets de los campos
        """
        model = Producto
        fields = [
            "categoria", "nombre", "marca", "modelo", 
            "descripcion", "especificaciones", "precio", 
            "stock", "imagen_url"
        ]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 3, "placeholder": "Descripción detallada del producto"}),
            "especificaciones": forms.Textarea(attrs={"rows": 2, "placeholder": "Características técnicas"}),
        }

class CategoriaForm(forms.ModelForm):
    """
    Formulario para crear y editar categorías.
    
    Incluye los campos básicos para la gestión de categorías de productos.
    """
    class Meta:
        """
        Configuración del formulario de categorías.
        
        Atributos:
            model: Modelo Categoria
            fields: Campos a incluir en el formulario
        """
        model = Categoria
        fields = ["nombre", "descripcion"]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 2, "placeholder": "Descripción de la categoría"}),
        }
