"""
Pruebas unitarias y de integración para la aplicación de tienda.

Este módulo contiene pruebas automatizadas para validar el correcto funcionamiento
de los modelos, vistas y lógica de negocio de la aplicación de tienda.
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Categoria, Producto, Carrito, ItemCarrito

# Clase base para configurar datos de prueba comunes
class TestBase(TestCase):
    """Configuración común para todas las pruebas."""
    
    @classmethod
    def setUpTestData(cls):
        """Configura datos de prueba que se comparten entre múltiples pruebas."""
        # Crear usuario de prueba
        cls.usuario = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Crear categoría de prueba
        cls.categoria = Categoria.objects.create(
            nombre='Electrónicos',
            descripcion='Dispositivos electrónicos varios'
        )
        
        # Crear producto de prueba
        cls.producto = Producto.objects.create(
            categoria=cls.categoria,
            nombre='Smartphone X',
            marca='TechBrand',
            modelo='X-1000',
            descripcion='Último modelo de smartphone',
            precio=999.99,
            stock=10
        )


class ModelTests(TestBase):
    """Pruebas para los modelos de la aplicación."""
    
    def test_creacion_categoria(self):
        """Verifica que se pueda crear una categoría correctamente."""
        self.assertEqual(self.categoria.nombre, 'Electrónicos')
        self.assertEqual(str(self.categoria), 'Electrónicos')
    
    def test_creacion_producto(self):
        """Verifica que se pueda crear un producto correctamente."""
        self.assertEqual(self.producto.nombre, 'Smartphone X')
        self.assertEqual(self.producto.precio, 999.99)
        self.assertEqual(str(self.producto), 'Smartphone X (TechBrand X-1000)')


class ViewTests(TestBase):
    """Pruebas para las vistas de la aplicación."""
    
    def test_vista_catalogo(self):
        """Verifica que la vista del catálogo se cargue correctamente."""
        response = self.client.get(reverse('catalogo'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tienda/catalogo.html')
    
    def test_vista_detalle_producto(self):
        """Verifica que la vista de detalle de producto funcione correctamente."""
        response = self.client.get(reverse('producto_detalle', args=[self.producto.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tienda/producto_detalle.html')


class CarritoTests(TestBase):
    """Pruebas para la funcionalidad del carrito de compras."""
    
    def test_agregar_al_carrito(self):
        """Verifica que se puedan agregar productos al carrito."""
        # Iniciar sesión como usuario de prueba
        self.client.login(username='testuser', password='testpass123')
        
        # Agregar producto al carrito
        response = self.client.post(
            reverse('agregar_al_carrito', args=[self.producto.pk]),
            {'cantidad': 2},
            follow=True
        )
        
        # Verificar que la redirección fue exitosa
        self.assertEqual(response.status_code, 200)
        
        # Verificar que el carrito se creó y tiene el producto
        carrito = Carrito.objects.get(usuario=self.usuario)
        self.assertEqual(carrito.items.count(), 1)
        self.assertEqual(carrito.items.first().cantidad, 2)


# Nota: Se pueden agregar más pruebas según sea necesario, incluyendo:
# - Pruebas de autenticación y autorización
# - Pruebas de formularios
# - Pruebas de la API del carrito
# - Pruebas de integración más complejas
