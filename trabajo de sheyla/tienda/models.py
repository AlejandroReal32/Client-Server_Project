"""
Modelos de datos para la aplicación de tienda en línea.

Este archivo define la estructura de la base de datos, incluyendo:
- Categorías de productos
- Productos
- Carrito de compras
- Ítems del carrito
"""
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Categoria(models.Model):
    """
    Modelo que representa una categoría de productos.
    
    Atributos:
        nombre: Nombre único de la categoría (ej: 'Laptops', 'Smartphones')
        descripcion: Descripción detallada de la categoría (opcional)
        creado: Fecha y hora de creación (automático)
        actualizado: Fecha y hora de última actualización (automático)
    """
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['-creado']
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

class Producto(models.Model):
    """
    Modelo que representa un producto en la tienda.
    
    Atributos:
        categoria: Relación con la categoría del producto
        nombre: Nombre del producto
        marca: Marca del fabricante
        modelo: Modelo específico
        descripcion: Descripción detallada
        especificaciones: Características técnicas (opcional)
        precio: Precio con 2 decimales
        stock: Cantidad disponible en inventario
        imagen_url: URL de la imagen del producto (opcional)
        creado: Fecha de creación (automático)
        actualizado: Fecha de última actualización (automático)
    """
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')
    nombre = models.CharField(max_length=200)
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    descripcion = models.TextField()
    especificaciones = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    imagen_url = models.URLField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} ({self.marca} {self.modelo})"

    class Meta:
        ordering = ['-creado']
        verbose_name_plural = 'Productos'

class Carrito(models.Model):
    """
    Modelo que representa el carrito de compras de un usuario.
    
    Atributos:
        usuario: Relación uno a uno con el usuario dueño del carrito
        productos: Relación muchos a muchos con Producto a través de ItemCarrito
        creado: Fecha de creación del carrito (automático)
        actualizado: Fecha de última actualización (automático)
        
    Propiedades:
        total: Calcula el monto total del carrito
        cantidad_items: Cuenta la cantidad total de ítems
    """
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    productos = models.ManyToManyField(Producto, through='ItemCarrito')
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Carrito de {self.usuario.username}'

    @property
    def total(self):
        """
        Calcula el monto total del carrito sumando los subtotales de cada ítem.
        
        Returns:
            Decimal: Suma total de los precios de los productos en el carrito
        """
        return sum(item.subtotal for item in self.items.all())

    @property
    def cantidad_items(self):
        """
        Calcula la cantidad total de ítems en el carrito.
        
        Returns:
            int: Suma de las cantidades de todos los ítems
        """
        return sum(item.cantidad for item in self.items.all())

    class Meta:
        """
        Configuraciones adicionales para el modelo Carrito.
        """
        verbose_name = 'Carrito de compras'
        verbose_name_plural = 'Carritos de compras'
        ordering = ['-creado']

class ItemCarrito(models.Model):
    """
    Modelo que representa un ítem dentro del carrito de compras.
    
    Atributos:
        carrito: Referencia al carrito al que pertenece
        producto: Producto específico en el carrito
        cantidad: Cantidad seleccionada del producto
        creado: Fecha de creación (automático)
        actualizado: Fecha de última actualización (automático)
        
    Propiedades:
        subtotal: Calcula el subtotal (precio * cantidad)
    """
    carrito = models.ForeignKey(Carrito, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.cantidad}x {self.producto.nombre} en carrito'

    @property
    def subtotal(self):
        """
        Calcula el subtotal del ítem multiplicando el precio del producto por la cantidad.
        
        Returns:
            Decimal: Precio total del ítem (precio unitario * cantidad)
        """
        return self.producto.precio * self.cantidad
