# Documentación del Proyecto - Tienda en Línea

## Tabla de Contenidos
1. [Estructura del Proyecto](#estructura-del-proyecto)
2. [Requisitos del Sistema](#requisitos-del-sistema)
3. [Modelos de Datos](#modelos-de-datos)
4. [Vistas y URLs](#vistas-y-urls)
5. [Formularios](#formularios)
6. [Carrito de Compras](#carrito-de-compras)
7. [Autenticación](#autenticación)
8. [Panel de Administración](#panel-de-administración)

## Estructura del Proyecto

```
.
├── db.sqlite3         # Base de datos SQLite
├── manage.py         # Script de administración de Django
├── requirements.txt  # Dependencias del proyecto
├── pcstore/          # Configuración principal del proyecto
├── staticfiles/      # Archivos estáticos recopilados
└── tienda/          # Aplicación principal
    ├── migrations/   # Migraciones de la base de datos
    ├── static/       # Archivos estáticos (CSS, JS, imágenes)
    ├── templates/    # Plantillas HTML
    ├── admin.py      # Configuración del admin de Django
    ├── apps.py       # Configuración de la aplicación
    ├── forms.py      # Formularios
    ├── models.py     # Modelos de datos
    ├── urls.py       # Rutas de la aplicación
    └── views.py      # Vistas de la aplicación
```

## Requisitos del Sistema

### Dependencias (requirements.txt)
```
Django>=5.2         # Framework web principal
crispy-forms>=2.0   # Para formularios con mejor presentación
```

## Modelos de Datos

### Categoria
- **Campos**:
  - `nombre`: Nombre único de la categoría
  - `descripcion`: Descripción opcional
  - `creado`: Fecha de creación
  - `actualizado`: Fecha de última actualización

### Producto
- **Campos**:
  - `categoria`: Relación con Categoría (clave foránea)
  - `nombre`, `marca`, `modelo`: Información básica
  - `precio`: Precio con 2 decimales
  - `stock`: Cantidad disponible
  - `imagen_url`: URL de la imagen del producto

### Carrito e ItemCarrito
- **Carrito**:
  - `usuario`: Relación uno a uno con el usuario
  - `productos`: Relación muchos a muchos con Producto a través de ItemCarrito
  - Métodos: `total` y `cantidad_items`

- **ItemCarrito**:
  - `carrito`: Relación con Carrito
  - `producto`: Relación con Producto
  - `cantidad`: Cantidad del producto en el carrito
  - Método: `subtotal` (precio * cantidad)

## Vistas y URLs

### URLs Públicas
- `/`: Catálogo de productos
- `/login/`: Inicio de sesión
- `/registro/`: Registro de usuarios
- `/producto/<id>/`: Detalles de producto
- `/carrito/`: Ver carrito

### URLs de Carrito
- `/carrito/agregar/<id>/`: Añadir al carrito
- `/carrito/actualizar/<id>/`: Actualizar cantidad
- `/carrito/eliminar/<id>/`: Eliminar ítem
- `/carrito/vaciar/`: Vaciar carrito
- `/carrito/checkout/`: Procesar pago

### URLs de Administración
- `/admin/producto/nuevo/`: Nuevo producto
- `/admin/producto/<id>/editar/`: Editar producto
- `/admin/categorias/`: Listar categorías
- `/admin/categoria/nueva/`: Nueva categoría

## Formularios

### RegistroUsuarioForm
- **Campos**: username, email, password1, password2
- **Uso**: Registro de nuevos usuarios

### ProductoForm
- **Campos**:
  - categoria, nombre, marca, modelo
  - descripcion, especificaciones
  - precio, stock, imagen_url
- **Widgets personalizados** para áreas de texto

### CategoriaForm
- **Campos**: nombre, descripcion
- **Uso**: Crear/editar categorías

## Carrito de Compras

### Funcionalidades
- Añadir/eliminar productos
- Actualizar cantidades
- Vaciar carrito
- Calcular totales
- Validación de stock

### API de Carrito
- `/api/carrito/cantidad/`: Obtener cantidad de ítems en carrito

## Autenticación

### Características
- Registro de usuarios
- Inicio/cierre de sesión
- Acceso restringido para ciertas funciones
- Redirección post-login

## Panel de Administración

### Gestión de Productos
- Crear/editar/eliminar productos
- Control de inventario

### Gestión de Categorías
- Crear/editar/eliminar categorías
- Asignación de productos a categorías

---
*Documentación generada automáticamente el 10/08/2025*
