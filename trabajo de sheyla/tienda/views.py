"""
Vistas para la aplicación de tienda en línea.

Este archivo contiene la lógica de negocio para:
- Catálogo de productos
- Autenticación de usuarios
- Gestión del carrito de compras
- Panel de administración
"""
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.views.decorators.http import require_POST, require_http_methods
from django.db.models import F
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q, F, Sum
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Producto, Categoria, Carrito, ItemCarrito
from .forms import ProductoForm, CategoriaForm, RegistroUsuarioForm

def es_admin(user):
    # Verifica si un usuario es administrador
    # 
    # Args:
    #     user: Usuario a verificar
     
    # Returns:
    #     bool: True si el usuario es administrador, False en caso contrario
    return user.is_staff

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def catalogo(request):
    # Muestra el catálogo de productos disponibles
    # 
    # Filtros soportados:
    # - Por categoría
    # - Búsqueda por texto (nombre, marca o modelo)
    #
    # Paginación: 12 productos por página
    
    # Obtener todas las categorías para el menú de filtrado
    categorias = Categoria.objects.all()
    # Filtrar solo productos con stock disponible, ordenados por fecha de creación
    productos_list = Producto.objects.filter(stock__gt=0).order_by('-creado')
    
    # Filtros
    categoria_id = request.GET.get('categoria')
    q = request.GET.get('q')
    
    if categoria_id:
        productos_list = productos_list.filter(categoria_id=categoria_id)
    if q:
        productos_list = productos_list.filter(
            Q(nombre__icontains=q) | Q(marca__icontains=q) | Q(modelo__icontains=q)
        )
    
    # Paginación
    page = request.GET.get('page', 1)
    paginator = Paginator(productos_list, 12)  # 12 productos por página
    
    try:
        productos = paginator.page(page)
    except PageNotAnInteger:
        productos = paginator.page(1)
    except EmptyPage:
        productos = paginator.page(paginator.num_pages)
    
    return render(request, 'tienda/catalogo.html', {
        'categorias': categorias,
        'productos': productos,
        'query': q or ''
    })

def login_view(request):
    # Muestra el formulario de inicio de sesión
    # 
    # Si el usuario ya está autenticado, redirige al catálogo
    # Si las credenciales son válidas, inicia sesión y redirige
    # Si las credenciales son inválidas, muestra un mensaje de error
    if request.user.is_authenticated:
        return redirect('catalogo')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'catalogo')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    # Create a simple form context for manual rendering
    form = AuthenticationForm()
    context = {
        'form': form,
        'username': form['username'],
        'password': form['password'],
    }
    return render(request, 'tienda/login.html', context)

from django.views.generic import View
from django.contrib.auth import logout as auth_logout

class CustomLogoutView(View):
    # Vista personalizada para cerrar sesión
    # 
    # Maneja tanto peticiones GET como POST para cerrar la sesión
    # Muestra un mensaje de confirmación y redirige al catálogo
    def get(self, request, *args, **kwargs):
        # Maneja peticiones GET para cerrar sesión
        return self.post(request, *args, **kwargs)
        
    def post(self, request, *args, **kwargs):
        # Maneja peticiones POST para cerrar sesión
        # 
        # Cierra la sesión del usuario, muestra un mensaje de éxito
        # y redirige al catálogo
        auth_logout(request)
        messages.success(request, 'Has cerrado sesión correctamente.')
        return redirect('catalogo')

@login_required
def agregar_al_carrito(request, producto_id):
    # Añade un producto al carrito del usuario
    # 
    # Si el producto ya está en el carrito, incrementa su cantidad
    # Si no hay suficiente stock, muestra un mensaje de error
    
    # Obtener el producto o devolver 404 si no existe
    producto = get_object_or_404(Producto, id=producto_id)
    # Obtener o crear el carrito del usuario
    carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    
    # Verificar si el producto ya está en el carrito
    try:
        item_carrito = ItemCarrito.objects.get(carrito=carrito, producto=producto)
        # Si el producto ya está en el carrito, incrementar la cantidad
        if item_carrito.cantidad < producto.stock:  # Verificar stock disponible
            item_carrito.cantidad += 1
            item_carrito.save()
            messages.success(request, f'Se ha añadido otra unidad de {producto.nombre} al carrito.')
        else:
            messages.warning(request, f'No hay suficiente stock de {producto.nombre}.')
    except ItemCarrito.DoesNotExist:
        # Si el producto no está en el carrito, crearlo con cantidad 1
        ItemCarrito.objects.create(
            carrito=carrito,
            producto=producto,
            cantidad=1
        )
        messages.success(request, f'Se ha añadido {producto.nombre} al carrito.')
    
    # Forzar la actualización del carrito
    carrito = Carrito.objects.get(usuario=request.user)
    return redirect('ver_carrito')

@login_required
def ver_carrito(request):
    # Muestra el contenido del carrito del usuario actual
    # 
    # Calcula los subtotales y el total de la compra
    
    # Obtener o crear el carrito del usuario
    carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    # Obtener todos los ítems del carrito con sus productos relacionados
    items = carrito.items.select_related('producto').all()
    
    # Crear una lista de tuplas (item, subtotal) para pasar a la plantilla
    items_con_subtotal = [
        (item, item.cantidad * item.producto.precio)
        for item in items
    ]
    
    # Calcular el total sumando todos los subtotales
    total = sum(subtotal for _, subtotal in items_con_subtotal)
    
    return render(request, 'tienda/carrito.html', {
        'items_con_subtotal': items_con_subtotal,
        'total': total,
    })

@require_POST
def actualizar_carrito(request, item_id):
    # Actualiza la cantidad de un ítem en el carrito
    # 
    # Soporta tres acciones:
    # - increase: Incrementa la cantidad en 1
    # - decrease: Disminuye la cantidad en 1
    # - update: Actualiza a una cantidad específica
    
    # Obtener el ítem o devolver 404 si no existe o no pertenece al usuario
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    # Obtener la acción a realizar (increase, decrease o update)
    action = request.POST.get('action')
    
    if action == 'increase':
        if item.cantidad < item.producto.stock:
            item.cantidad += 1
            item.save()
            messages.success(request, f'Se ha incrementado la cantidad de {item.producto.nombre}')
        else:
            messages.warning(request, f'No hay suficiente stock de {item.producto.nombre}. Stock disponible: {item.producto.stock}')
    elif action == 'decrease':
        if item.cantidad > 1:
            item.cantidad -= 1
            item.save()
            messages.success(request, f'Se ha reducido la cantidad de {item.producto.nombre}')
        else:
            item.delete()
            messages.success(request, f'{item.producto.nombre} eliminado del carrito')
    else:
        # Actualización manual del campo de cantidad
        try:
            nueva_cantidad = int(request.POST.get('cantidad', 1))
            if nueva_cantidad <= 0:
                item.delete()
                messages.success(request, f'{item.producto.nombre} eliminado del carrito')
            elif nueva_cantidad > item.producto.stock:
                messages.warning(request, f'No hay suficiente stock de {item.producto.nombre}. Stock disponible: {item.producto.stock}')
            else:
                item.cantidad = nueva_cantidad
                item.save()
                messages.success(request, f'Cantidad actualizada para {item.producto.nombre}')
        except (ValueError, TypeError):
            messages.error(request, 'Cantidad no válida')
    
    return redirect('ver_carrito')

@require_POST
def eliminar_del_carrito(request, item_id):
    # Elimina un ítem del carrito
    # 
    # Args:
    #     request: Objeto HttpRequest
    #     item_id: ID del ítem a eliminar
        
    # Obtener el ítem o devolver 404 si no existe o no pertenece al usuario
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    nombre_producto = item.producto.nombre
    # Eliminar el ítem del carrito
    item.delete()
    # Mostrar mensaje de confirmación
    messages.success(request, f'{nombre_producto} eliminado del carrito')
    return redirect('ver_carrito')

@require_POST
def vaciar_carrito(request):
    # Vacía completamente el carrito del usuario
    # 
    # Elimina todos los ítems del carrito y muestra un mensaje de confirmación
    
    # Obtener el carrito del usuario o 404 si no existe
    carrito = get_object_or_404(Carrito, usuario=request.user)
    # Eliminar todos los ítems del carrito
    carrito.items.all().delete()
    # Mostrar mensaje de confirmación
    messages.success(request, 'El carrito ha sido vaciado')
    return redirect('ver_carrito')

def procesar_pago(request):
    # Procesa el pago de los productos en el carrito
    # 
    # Verifica el stock de los productos antes de procesar el pago
    # Si algún producto no tiene suficiente stock, muestra un error
    
    # Obtener el carrito del usuario
    carrito = get_object_or_404(Carrito, usuario=request.user)
    # Obtener todos los ítems del carrito con sus productos
    items = carrito.items.select_related('producto').all()
    
    # Verificar que hay productos en el carrito
    if not items:
        messages.warning(request, 'No hay productos en el carrito')
        return redirect('ver_carrito')
    
    # Verificar stock antes de procesar el pago
    for item in items:
        if item.cantidad > item.producto.stock:
            messages.error(request, f'No hay suficiente stock de {item.producto.nombre}. Stock disponible: {item.producto.stock}')
            return redirect('ver_carrito')
    
    # Aquí iría la lógica de pago real
    # Por ahora, solo vaciamos el carrito y mostramos un mensaje de éxito
    
    # Actualizar el stock
    for item in items:
        producto = item.producto
        producto.stock -= item.cantidad
        producto.save()
    
    # Vaciar el carrito
    carrito.items.all().delete()
    
    messages.success(request, '¡Pago procesado con éxito! Gracias por tu compra.')
    return redirect('catalogo')

def registro(request):
    # Maneja el registro de nuevos usuarios
    # 
    # Si el formulario es válido, crea un nuevo usuario, inicia sesión
    # automáticamente y redirige al catálogo
    
    if request.user.is_authenticated:
        return redirect('catalogo')
    
    if request.method == 'POST':
        # Procesar el formulario de registro
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            # Guardar el nuevo usuario
            user = form.save()
            # Iniciar sesión automáticamente después del registro
            login(request, user)
            messages.success(request, '¡Registro exitoso! Ahora estás conectado.')
            return redirect('catalogo')
    else:
        # Mostrar el formulario de registro vacío
        form = RegistroUsuarioForm()
    return render(request, 'tienda/registro.html', {'form': form})

def producto_detalle(request, pk):
    # Muestra los detalles de un producto específico
    #
    # Args:
    #     request: Objeto HttpRequest
    #     pk: ID del producto a mostrar
    #     
    # Returns:
    #     HttpResponse: Renderiza la plantilla con los detalles del producto
    producto = get_object_or_404(Producto, pk=pk)
    return render(request, 'tienda/producto_detalle.html', {'producto': producto})

@login_required
@user_passes_test(es_admin)
def producto_nuevo(request):
    # Crea un nuevo producto (solo para administradores)
    #
    # Muestra un formulario para crear un nuevo producto
    # Si el formulario es válido, guarda el producto y redirige a sus detalles
    if request.method == "POST":
        # Procesar el formulario con los datos y archivos enviados
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            # Guardar el nuevo producto
            producto = form.save()
            messages.success(request, 'Producto creado exitosamente.')
            # Redirigir a la página de detalles del nuevo producto
            return redirect('producto_detalle', pk=producto.pk)
    else:
        # Mostrar formulario vacío para crear un nuevo producto
        form = ProductoForm()
    # Renderizar la plantilla con el formulario
    return render(request, 'tienda/producto_editar.html', {'form': form, 'titulo': 'Nuevo Producto'})

@login_required
@user_passes_test(es_admin)
def producto_editar(request, pk):
    # Edita un producto existente (solo para administradores)
    # 
    # Muestra un formulario prellenado con los datos del producto
    # Si el formulario es válido, actualiza el producto y redirige a sus detalles
    # 
    # Args:
    #     request: Objeto HttpRequest
    #     pk: ID del producto a editar
    #     
    # Returns:
    #     HttpResponse: Renderiza el formulario de producto o redirige a los detalles
    # Obtener el producto o devolver 404 si no existe
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == "POST":
        # Procesar el formulario con los datos y archivos enviados
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            # Actualizar el producto con los nuevos datos
            producto = form.save()
            messages.success(request, 'Producto actualizado exitosamente.')
            # Redirigir a la página de detalles del producto actualizado
            return redirect('producto_detalle', pk=producto.pk)
    else:
        # Mostrar formulario prellenado con los datos actuales del producto
        form = ProductoForm(instance=producto)
    
    # Renderizar la plantilla con el formulario
    return render(request, 'tienda/producto_editar.html', {'form': form, 'titulo': 'Editar Producto'})

@login_required
@user_passes_test(es_admin)
def producto_eliminar(request, pk):
    # Elimina un producto existente (solo para administradores)
    # 
    # Muestra un mensaje de confirmación antes de eliminar el producto
    # 
    # Args:
    #     request: Objeto HttpRequest
    #     pk: ID del producto a eliminar
    #     
    # Returns:
    #     HttpResponse: Renderiza la página de confirmación o elimina el producto
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        # Eliminar el producto
        producto.delete()
        # Mostrar mensaje de éxito
        messages.success(request, 'Producto eliminado correctamente')
        # Redirigir al catálogo
        return redirect('catalogo')
        
    # Mostrar la página de confirmación de eliminación
    return render(request, 'tienda/producto_eliminar.html', {'producto': producto})

@login_required
@user_passes_test(es_admin)
def categorias(request):
    # Muestra la lista de todas las categorías (solo para administradores)
    # 
    # Returns:
    #     HttpResponse: Renderiza la plantilla con la lista de categorías
    # Obtener todas las categorías ordenadas por nombre
    categorias = Categoria.objects.all().order_by('nombre')
    # Renderizar la plantilla con las categorías
    return render(request, 'tienda/categorias.html', {'categorias': categorias})

@login_required
@user_passes_test(es_admin)
def categoria_nueva(request):
    """
    Crea una nueva categoría (solo para administradores).
    
    Muestra un formulario para crear una nueva categoría.
    Si el formulario es válido, guarda la categoría y redirige a la lista de categorías.
    
    Returns:
        HttpResponse: Renderiza el formulario de categoría o redirige a la lista
    """
    if request.method == "POST":
        # Procesar el formulario con los datos enviados
        form = CategoriaForm(request.POST)
        if form.is_valid():
            # Guardar la nueva categoría
            form.save()
            messages.success(request, 'Categoría creada exitosamente.')
            # Redirigir a la lista de categorías
            return redirect('categorias')
    else:
        # Mostrar formulario vacío para crear una nueva categoría
        form = CategoriaForm()
    # Renderizar la plantilla con el formulario
    return render(request, 'tienda/categoria_editar.html', 
                 {'form': form, 'titulo': 'Nueva Categoría'})

@login_required
@user_passes_test(es_admin)
def categoria_editar(request, pk):
    """
    Edita una categoría existente (solo para administradores).
    
    Muestra un formulario prellenado con los datos de la categoría.
    Si el formulario es válido, actualiza la categoría y redirige a la lista de categorías.
    
    Args:
        request: Objeto HttpRequest
        pk: ID de la categoría a editar
        
    Returns:
        HttpResponse: Renderiza el formulario de categoría o redirige a la lista
    """
    # Obtener la categoría o devolver 404 si no existe
    categoria = get_object_or_404(Categoria, pk=pk)
    
    if request.method == 'POST':
        # Procesar el formulario con los datos enviados
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            # Guardar los cambios en la categoría
            form.save()
            # Mostrar mensaje de éxito
            messages.success(request, 'Categoría actualizada exitosamente.')
            # Redirigir a la lista de categorías
            return redirect('categorias')
    else:
        # Mostrar formulario prellenado con los datos actuales de la categoría
        form = CategoriaForm(instance=categoria)
    
    # Renderizar la plantilla con el formulario
    return render(request, 'tienda/categoria_editar.html', 
                 {'form': form, 'titulo': 'Editar Categoría'})

@login_required
@user_passes_test(es_admin)
def categoria_eliminar(request, pk):
    """
    Elimina una categoría existente (solo para administradores).
    
    Muestra una página de confirmación antes de eliminar la categoría.
    Si se confirma, elimina la categoría y redirige a la lista de categorías.
    
    Args:
        request: Objeto HttpRequest
        pk: ID de la categoría a eliminar
        
    Returns:
        HttpResponse: Renderiza la página de confirmación o redirige a la lista
    """
    # Obtener la categoría o devolver 404 si no existe
    categoria = get_object_or_404(Categoria, pk=pk)
    
    if request.method == 'POST':
        # Eliminar la categoría
        categoria.delete()
        # Mostrar mensaje de éxito
        messages.success(request, 'Categoría eliminada correctamente')
        # Redirigir a la lista de categorías
        return redirect('categorias')
    
    # Mostrar la página de confirmación de eliminación
    return render(request, 'tienda/categoria_eliminar.html', 
                 {'categoria': categoria})

@login_required
def api_carrito_cantidad(request):
    """
    Vista de API que devuelve la cantidad de ítems en el carrito del usuario actual.
    
    Utilizada para actualizar el contador del carrito en la interfaz de usuario
    sin necesidad de recargar la página.
    
    Args:
        request: Objeto HttpRequest
        
    Returns:
        JsonResponse: Objeto JSON con la cantidad de ítems en el carrito
        
    Ejemplo de respuesta:
        {"cantidad": 3}
    """
    try:
        # Obtener el carrito del usuario
        carrito = Carrito.objects.get(usuario=request.user)
        # Calcular la cantidad total de ítems en el carrito
        cantidad = carrito.items.aggregate(total=Sum('cantidad'))['total'] or 0
    except Carrito.DoesNotExist:
        # Si el carrito no existe, la cantidad es 0
        cantidad = 0
    except Exception as e:
        # En caso de cualquier otro error, registrar y devolver error 500
        return JsonResponse({
            'cantidad': 0,
            'message': f'Error al obtener la cantidad de ítems en el carrito: {str(e)}'
        }, status=500)
    
    # Devolver la cantidad como respuesta JSON
    return JsonResponse({'cantidad': cantidad})
