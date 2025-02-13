from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Dependencia, Recurso, Prestamo, Usuario
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.hashers import make_password

# Vista de inicio
@login_required
def inicio(request):
    if request.user.rol == 'admin':
        context = {
            'total_recursos': Recurso.objects.filter(dependencia=request.user.dependencia_admin).count(),
            'prestamos_activos': Prestamo.objects.filter(
                recurso__dependencia=request.user.dependencia_admin,
                devuelto=False
            ).count(),
            'prestamos_recientes': Prestamo.objects.filter(
                recurso__dependencia=request.user.dependencia_admin
            ).order_by('-fecha_prestamo')[:10]
        }
        return render(request, 'admin/dashboard.html', context)
    elif request.user.rol == 'profesor':
        return render(request, 'profesor/dashboard.html')
    else:  # estudiante
        return render(request, 'estudiante/dashboard.html')

# Vista de recursos por dependencia
@login_required
def inventario(request):
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permiso para acceder a esta página')
        return redirect('inicio')
    
    recursos = Recurso.objects.filter(dependencia=request.user.dependencia_admin)
    return render(request, 'admin/inventario/lista.html', {'recursos': recursos})

@login_required
def agregar_recurso(request):
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permiso para acceder a esta página')
        return redirect('inicio')
    
    if request.method == 'POST':
        try:
            Recurso.objects.create(
                nombre=request.POST['nombre'],
                descripcion=request.POST['descripcion'],
                color=request.POST['color'],
                foto=request.FILES.get('foto'),
                dependencia=request.user.dependencia_admin
            )
            messages.success(request, 'Recurso agregado exitosamente')
            return redirect('inventario')
        except Exception as e:
            messages.error(request, f'Error al crear el recurso: {str(e)}')
    
    return render(request, 'admin/inventario/agregar.html')

@login_required
def editar_recurso(request, recurso_id):
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permiso para acceder a esta página')
        return redirect('inicio')
    
    recurso = get_object_or_404(Recurso, id=recurso_id, dependencia=request.user.dependencia_admin)
    
    if request.method == 'POST':
        try:
            recurso.nombre = request.POST['nombre']
            recurso.descripcion = request.POST['descripcion']
            recurso.color = request.POST['color']
            if 'foto' in request.FILES:
                recurso.foto = request.FILES['foto']
            recurso.save()
            messages.success(request, 'Recurso actualizado exitosamente')
            return redirect('inventario')
        except Exception as e:
            messages.error(request, f'Error al actualizar el recurso: {str(e)}')
    
    return render(request, 'admin/inventario/editar.html', {'recurso': recurso})

@login_required
def eliminar_recurso(request, recurso_id):
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permiso para acceder a esta página')
        return redirect('inicio')
    
    recurso = get_object_or_404(Recurso, id=recurso_id, dependencia=request.user.dependencia_admin)
    
    if request.method == 'POST':
        try:
            recurso.delete()
            messages.success(request, 'Recurso eliminado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al eliminar el recurso: {str(e)}')
    
    return redirect('inventario')

@login_required
def recursos_no_disponibles(request):
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permiso para acceder a esta página')
        return redirect('inicio')
    
    recursos = Recurso.objects.filter(
        dependencia=request.user.dependencia_admin,
        disponible=False
    )
    return render(request, 'admin/inventario/no_disponibles.html', {'recursos': recursos})

# Vista para crear un préstamo
@login_required
def crear_prestamo(request, recurso_id):
    recurso = get_object_or_404(Recurso, id=recurso_id, disponible=True)
    if request.method == 'POST':
        fecha_devolucion = request.POST.get('fecha_devolucion')
        firma = request.FILES.get('firma')
        Prestamo.objects.create(
            usuario=request.user,
            recurso=recurso,
            fecha_devolucion=fecha_devolucion,
            firmado=firma
        )
        recurso.disponible = False
        recurso.save()
        return redirect('inicio')
    return render(request, 'crear_prestamo.html', {'recurso': recurso})

# Vista para ver préstamos pendientes
@login_required
def prestamos_pendientes(request):
    prestamos = Prestamo.objects.filter(usuario=request.user, devuelto=False)
    return render(request, 'prestamos_pendientes.html', {'prestamos': prestamos})

# ==========================
# 🔐 NUEVAS VISTAS PARA LOGIN/LOGOUT
# ==========================

# Vista para iniciar sesión
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Inicio de sesión exitoso")
            return redirect("inicio")  # Redirige al inicio después de iniciar sesión
        else:
            messages.error(request, "Usuario o contraseña incorrectos")

    return render(request, "login.html")

# Vista para cerrar sesión
def logout_view(request):
    logout(request)
    messages.success(request, "Has cerrado sesión correctamente")
    return redirect("login")  # Redirige al login después de cerrar sesión

# Vistas de Préstamos
@login_required
def prestamos_lista(request):
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permiso para acceder a esta página')
        return redirect('inicio')
    
    prestamos = Prestamo.objects.filter(
        recurso__dependencia=request.user.dependencia_admin
    ).order_by('-fecha_prestamo')
    return render(request, 'admin/prestamos/lista.html', {'prestamos': prestamos})

@login_required
def nuevo_prestamo(request):
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permiso para acceder a esta página')
        return redirect('inicio')
    
    if request.method == 'POST':
        try:
            usuario = Usuario.objects.get(id=request.POST['usuario'])
            recurso = Recurso.objects.get(
                id=request.POST['recurso'],
                dependencia=request.user.dependencia_admin,
                disponible=True
            )
            
            prestamo = Prestamo.objects.create(
                usuario=usuario,
                recurso=recurso,
                fecha_devolucion=request.POST['fecha_devolucion']
            )
            
            recurso.disponible = False
            recurso.save()
            
            messages.success(request, 'Préstamo registrado exitosamente')
            return redirect('prestamos_lista')
        except Exception as e:
            messages.error(request, f'Error al crear el préstamo: {str(e)}')
    
    context = {
        'usuarios': Usuario.objects.filter(rol__in=['estudiante', 'profesor']),
        'recursos': Recurso.objects.filter(dependencia=request.user.dependencia_admin, disponible=True)
    }
    return render(request, 'admin/prestamos/nuevo.html', context)

@login_required
def prestamos_activos(request):
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permiso para acceder a esta página')
        return redirect('inicio')
    
    prestamos = Prestamo.objects.filter(
        recurso__dependencia=request.user.dependencia_admin,
        devuelto=False
    ).order_by('fecha_devolucion')
    
    context = {
        'prestamos': prestamos,
        'now': timezone.now()
    }
    return render(request, 'admin/prestamos/activos.html', context)

@login_required
def historial_prestamos(request):
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permiso para acceder a esta página')
        return redirect('inicio')
    
    prestamos = Prestamo.objects.filter(
        recurso__dependencia=request.user.dependencia_admin,
        devuelto=True
    ).order_by('-fecha_prestamo')
    return render(request, 'admin/prestamos/historial.html', {'prestamos': prestamos})

@login_required
def editar_prestamo(request, prestamo_id):
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permiso para acceder a esta página')
        return redirect('inicio')
    
    prestamo = get_object_or_404(
        Prestamo,
        id=prestamo_id,
        recurso__dependencia=request.user.dependencia_admin
    )
    
    if request.method == 'POST':
        try:
            prestamo.fecha_devolucion = request.POST['fecha_devolucion']
            prestamo.save()
            messages.success(request, 'Préstamo actualizado exitosamente')
            return redirect('prestamos_lista')
        except Exception as e:
            messages.error(request, f'Error al actualizar el préstamo: {str(e)}')
    
    return render(request, 'admin/prestamos/editar.html', {'prestamo': prestamo})

@login_required
def marcar_devuelto(request, prestamo_id):
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permiso para acceder a esta página')
        return redirect('inicio')
    
    prestamo = get_object_or_404(
        Prestamo,
        id=prestamo_id,
        recurso__dependencia=request.user.dependencia_admin,
        devuelto=False
    )
    
    try:
        prestamo.devuelto = True
        prestamo.fecha_devuelto = timezone.now()
        prestamo.save()
        
        prestamo.recurso.disponible = True
        prestamo.recurso.save()
        
        messages.success(request, 'Préstamo marcado como devuelto exitosamente')
    except Exception as e:
        messages.error(request, f'Error al marcar el préstamo como devuelto: {str(e)}')
    
    return redirect('prestamos_lista')

def registro_view(request):
    if request.method == 'POST':
        # Obtener datos del formulario
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        codigo = request.POST.get('codigo')
        programa = request.POST.get('programa')
        rol = request.POST.get('rol')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Validaciones básicas
        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden")
            return redirect('registro')

        if Usuario.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya existe")
            return redirect('registro')

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, "El correo electrónico ya está registrado")
            return redirect('registro')

        if Usuario.objects.filter(codigo=codigo).exists():
            messages.error(request, "El código ya está registrado")
            return redirect('registro')

        # Crear usuario
        try:
            usuario = Usuario.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                codigo=codigo,
                programa=programa,
                rol=rol,
                password=make_password(password1)
            )
            messages.success(request, "Registro exitoso. Por favor inicia sesión.")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"Error al crear el usuario: {str(e)}")
            return redirect('registro')

    return render(request, 'registro.html')

@login_required
def solicitar_prestamo(request, recurso_id):
    recurso = get_object_or_404(Recurso, id=recurso_id)
    
    # Verificar si el recurso está disponible
    if not recurso.disponible:
        messages.error(request, "Este recurso no está disponible actualmente.")
        return redirect('inicio')
    
    # Verificar si el usuario ya tiene un préstamo activo de este recurso
    prestamo_activo = Prestamo.objects.filter(
        usuario=request.user,
        recurso=recurso,
        devuelto=False
    ).exists()
    
    if prestamo_activo:
        messages.error(request, "Ya tienes un préstamo activo de este recurso.")
        return redirect('inicio')
    
    if request.method == 'POST':
        # Crear el préstamo
        fecha_devolucion = datetime.now() + timedelta(days=7)  # Por defecto 7 días
        Prestamo.objects.create(
            usuario=request.user,
            recurso=recurso,
            fecha_devolucion=fecha_devolucion
        )
        
        # Actualizar el estado del recurso
        recurso.disponible = False
        recurso.save()
        
        messages.success(request, "Préstamo realizado con éxito.")
        return redirect('inicio')
    
    return render(request, 'prestamo/solicitar.html', {
        'recurso': recurso
    })
