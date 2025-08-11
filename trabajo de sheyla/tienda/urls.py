# Importaciones de Django y vistas propias
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

# Definición de patrones de URL para la aplicación tienda
urlpatterns = [
    # ====== RUTAS PÚBLICAS ======
    # Página principal - Catálogo de productos
    path('', views.catalogo, name='catalogo'),
    
    # Autenticación de usuarios
    path('login/', views.login_view, name='login'),  # Inicio de sesión
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),  # Cierre de sesión
    path('registro/', views.registro, name='registro'),  # Registro de nuevos usuarios
    
    # Detalles de un producto específico
    path('producto/<int:pk>/', views.producto_detalle, name='producto_detalle'),
    
    # ====== RUTAS DEL CARRITO DE COMPRAS ======
    # Gestión del carrito
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/actualizar/<int:item_id>/', views.actualizar_carrito, name='actualizar_carrito'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/vaciar/', views.vaciar_carrito, name='vaciar_carrito'),
    path('carrito/checkout/', views.procesar_pago, name='procesar_pago'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    
    # API para obtener la cantidad de items en el carrito (requiere autenticación)
    path('api/carrito/cantidad/', login_required(views.api_carrito_cantidad), name='api_carrito_cantidad'),
    
    # ====== RUTAS DE ADMINISTRACIÓN ======
    # Gestión de productos
    path('admin/producto/nuevo/', views.producto_nuevo, name='producto_nuevo'),
    path('admin/producto/<int:pk>/editar/', views.producto_editar, name='producto_editar'),
    path('admin/producto/<int:pk>/eliminar/', views.producto_eliminar, name='producto_eliminar'),
    
    # Gestión de categorías
    path('admin/categorias/', views.categorias, name='categorias'),
    path('admin/categoria/nueva/', views.categoria_nueva, name='categoria_nueva'),
    path('admin/categoria/<int:pk>/editar/', views.categoria_editar, name='categoria_editar'),
    path('admin/categoria/<int:pk>/eliminar/', views.categoria_eliminar, name='categoria_eliminar'),
]
