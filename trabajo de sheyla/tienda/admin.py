"""
Configuración del panel de administración de Django para la aplicación de tienda.

Este archivo define cómo se muestran y gestionan los modelos de la aplicación
desde el panel de administración de Django.
"""
from django.contrib import admin
from .models import Categoria, Producto, Carrito, ItemCarrito
from django.utils.html import format_html

class CategoriaAdmin(admin.ModelAdmin):
    """
    Configuración del administrador para el modelo Categoria.
    
    Atributos:
        list_display: Campos mostrados en la lista de categorías
        search_fields: Campos por los que se puede buscar
    """
    list_display = ('nombre', 'descripcion_corta')
    search_fields = ('nombre',)
    
    def descripcion_corta(self, obj):
        """
        Muestra una versión acortada de la descripción en la lista de categorías.
        
        Args:
            obj: Instancia de Categoria
            
        Returns:
            str: Descripción truncada a 50 caracteres o cadena vacía si no hay descripción
        """
        return f"{obj.descripcion[:50]}..." if obj.descripcion else ""
    descripcion_corta.short_description = 'Descripción'

class ProductoAdmin(admin.ModelAdmin):
    """
    Configuración del administrador para el modelo Producto.
    
    Atributos:
        list_display: Campos mostrados en la lista de productos
        list_filter: Filtros disponibles en el panel lateral
        search_fields: Campos por los que se puede buscar
        list_editable: Campos editables directamente desde la lista
        readonly_fields: Campos de solo lectura en el formulario de edición
        fieldsets: Agrupación lógica de campos en el formulario de edición
    """
    list_display = ('nombre', 'precio', 'stock', 'categoria', 'imagen_previa', 'creado')
    list_filter = ('categoria', 'marca')
    search_fields = ('nombre', 'descripcion', 'marca', 'modelo')
    list_editable = ('precio', 'stock')
    readonly_fields = ('creado', 'actualizado', 'imagen_previa')
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'categoria', 'marca', 'modelo')
        }),
        ('Precio e Inventario', {
            'fields': ('precio', 'stock', 'especificaciones')
        }),
        ('Imágenes', {
            'fields': ('imagen_url', 'imagen_previa')
        }),
        ('Fechas', {
            'fields': ('creado', 'actualizado'),
            'classes': ('collapse',)  # Sección colapsable
        }),
    )
    
    def imagen_previa(self, obj):
        """
        Muestra una miniatura de la imagen del producto en el administrador.
        
        Args:
            obj: Instancia de Producto
            
        Returns:
            str: Etiqueta HTML de la imagen o texto indicando que no hay imagen
        """
        if obj.imagen_url:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.imagen_url)
        return "Sin imagen"
    imagen_previa.short_description = 'Vista previa'

class ItemCarritoInline(admin.TabularInline):
    """
    Configuración en línea para los ítems del carrito en el administrador.
    
    Permite gestionar los ítems directamente desde la vista de edición del carrito.
    """
    model = ItemCarrito
    extra = 1  # Número de formularios vacíos adicionales mostrados
    readonly_fields = ('subtotal',)  # Campo calculado de solo lectura
    
    def subtotal(self, obj):
        """
        Calcula y muestra el subtotal para cada ítem en el carrito.
        
        Args:
            obj: Instancia de ItemCarrito
            
        Returns:
            str: Subtotal formateado como moneda
        """
        if obj and obj.producto:
            return f"${obj.cantidad * obj.producto.precio:.2f}"
        return "$0.00"
    subtotal.short_description = 'Subtotal'

class CarritoAdmin(admin.ModelAdmin):
    """
    Configuración del administrador para el modelo Carrito.
    
    Muestra los carritos con información relevante y permite gestionar
    los ítems a través de la interfaz en línea.
    """
    list_display = ('id', 'usuario', 'creado', 'total_carrito')
    inlines = [ItemCarritoInline]  # Incluye los ítems del carrito en la vista de edición
    readonly_fields = ('creado', 'actualizado')
    
    def total_carrito(self, obj):
        """
        Muestra el total del carrito formateado como moneda.
        
        Args:
            obj: Instancia de Carrito
            
        Returns:
            str: Total del carrito formateado
        """
        if hasattr(obj, 'items') and obj.items.exists():
            return f"${sum(item.cantidad * item.producto.precio for item in obj.items.all()):.2f}"
        return "$0.00"
    total_carrito.short_description = 'Total'

# Registrar modelos con sus clases de administración personalizadas
admin.site.register(Categoria, CategoriaAdmin)  # Registra Categoria con configuración personalizada
admin.site.register(Producto, ProductoAdmin)    # Registra Producto con configuración personalizada
admin.site.register(Carrito, CarritoAdmin)      # Registra Carrito con configuración personalizada
# No es necesario registrar ItemCarrito directamente ya que se muestra en línea con Carrito
# admin.site.register(ItemCarrito)
