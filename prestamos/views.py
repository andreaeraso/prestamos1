from datetime import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Dependencia, Recurso, Prestamo, Usuario, SolicitudPrestamo
from django.contrib.auth.hashers import make_password
from collections import defaultdict

# Vista de inicio
@login_required
def inicio(request):
    if request.user.rol == 'admin':
        context = {
            'total_recursos': Recurso.objects.filter(dependencia=request.user.dependencia_administrada).count(),
            'prestamos_activos': Prestamo.objects.filter(
                recurso__dependencia=request.user.dependencia_administrada,
                devuelto=False
            ).count(),
            'prestamos_recientes': Prestamo.objects.filter(
                recurso__dependencia=request.user.dependencia_administrada
            ).order_by('-fecha_prestamo')[:10]
        }
        return render(request, 'admin/dashboard.html', context)
    elif request.user.rol == 'profesor':
        return render(request, 'profesor/dashboard.html')
    else:  # estudiante
        return render(request, 'estudiante/dashboard.html')

# 🔐 NUEVAS VISTAS PARA LOGIN/LOGOUT
def registro_view(request): #Registro de un usuario
    if request.method == 'POST':
        # Obtener datos del formulario
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        codigo = request.POST.get('codigo')  # Este parece ser el identificador único
        programa = request.POST.get('programa')
        rol = request.POST.get('rol')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Validaciones básicas
        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden")
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
                email=email,
                first_name=first_name,
                last_name=last_name,
                codigo=codigo,  # Se usa código en lugar de username
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

# Vista de recursos por dependencia
@login_required
def inventario(request):
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permiso para acceder a esta página')
        return redirect('inicio')

    recursos_queryset = Recurso.objects.filter(dependencia=request.user.dependencia_administrada)

    # Agrupar los recursos por tipo
    recursos_agrupados = defaultdict(list)
    for recurso in recursos_queryset:
        recursos_agrupados[recurso.tipo].append(recurso)

    return render(request, 'admin/inventario/lista.html', {'recursos': dict(recursos_agrupados)})


@login_required
def agregar_recurso(request):
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permiso para acceder a esta página')
        return redirect('inicio')
    
    if request.method == 'POST':
        id_recurso = request.POST.get('id', '').strip()
        tipo = request.POST.get('tipo', '').strip()
        nombre = request.POST.get('nombre', '').strip()
        foto = request.FILES.get('foto', None)
        descripcion = request.POST.get('descripcion', '').strip()
        dependencia = request.user.dependencia_administrada  # Se asocia a la dependencia del usuario

        # Validar que los campos obligatorios no estén vacíos
        if not (id_recurso and tipo and nombre and descripcion):
            messages.error(request, 'Todos los campos son obligatorios excepto la foto')
            return redirect('agregar_recurso')

        try:
            Recurso.objects.create(
                id=id_recurso,
                tipo=tipo,
                nombre=nombre,
                foto=foto,
                descripcion=descripcion,
                dependencia=dependencia
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

    recurso = get_object_or_404(Recurso, id=recurso_id, dependencia=request.user.dependencia_administrada)

    if request.method == 'POST':
        try:
            nuevo_id = request.POST.get('id', '').strip()
            tipo = request.POST.get('tipo', '').strip()
            nombre = request.POST.get('nombre', '').strip()
            descripcion = request.POST.get('descripcion', '').strip()
            foto = request.FILES.get('foto', None)

            # Si el usuario intenta cambiar el ID
            if nuevo_id and str(nuevo_id) != str(recurso.id):
                if Recurso.objects.filter(id=nuevo_id).exists():
                    messages.error(request, 'El ID ya está en uso por otro recurso.')
                    return redirect('editar_recurso', recurso_id=recurso.id)

                # Crear un nuevo recurso con el nuevo ID
                nuevo_recurso = Recurso(
                    id=nuevo_id,
                    tipo=tipo,
                    nombre=nombre,
                    descripcion=descripcion,
                    dependencia=recurso.dependencia,  # Mantiene la dependencia
                    disponible=recurso.disponible,  # Mantiene el estado
                )

                # Si hay una nueva foto, usarla; de lo contrario, mantener la existente
                if foto:
                    nuevo_recurso.foto = foto
                else:
                    nuevo_recurso.foto = recurso.foto

                # Guardar el nuevo recurso
                nuevo_recurso.save()

                # Eliminar el recurso antiguo
                recurso.delete()

                messages.success(request, 'Recurso actualizado exitosamente con un nuevo ID.')
                return redirect('inventario')

            # Si no se cambia el ID, solo actualizar los datos
            recurso.tipo = tipo
            recurso.nombre = nombre
            recurso.descripcion = descripcion
            if foto:
                recurso.foto = foto  # Si se sube una nueva foto, actualizarla

            recurso.save()

            messages.success(request, 'Recurso actualizado exitosamente.')
            return redirect('inventario')

        except Exception as e:
            messages.error(request, f'Error al actualizar el recurso: {str(e)}')

    return render(request, 'admin/inventario/editar.html', {'recurso': recurso})

@login_required
def eliminar_recurso(request, recurso_id):
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permiso para acceder a esta página')
        return redirect('inicio')
    
    recurso = get_object_or_404(Recurso, id=recurso_id, dependencia=request.user.dependencia_administrada)
    
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
        dependencia=request.user.dependencia_administrada,
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

#####################################################################################

# Vistas de Préstamos
@login_required
def prestamos_lista(request):
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permiso para acceder a esta página')
        return redirect('inicio')
    
    prestamos = Prestamo.objects.filter(
        recurso__dependencia=request.user.dependencia_administrada
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
                dependencia=request.user.dependencia_administrada,
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
        'recursos': Recurso.objects.filter(dependencia=request.user.dependencia_administrada, disponible=True)
    }
    return render(request, 'admin/prestamos/nuevo.html', context)

@login_required
def prestamos_activos(request):
    if request.user.rol != 'admin':
        messages.error(request, 'No tienes permiso para acceder a esta página')
        return redirect('inicio')
    
    prestamos = Prestamo.objects.filter(
        recurso__dependencia=request.user.dependencia_administrada,
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
        recurso__dependencia=request.user.dependencia_administrada,
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
        recurso__dependencia=request.user.dependencia_administrada
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
        recurso__dependencia=request.user.dependencia_administrada,
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

## Visualizacion de los recursos y las dependecias
@login_required
def lista_dependencias(request): #Esta lista es la que se muestra en la pagina del estudiante al darle solicitar prestamo
    if request.user.rol != 'estudiante':
        messages.error(request, 'No tienes permiso para acceder a esta página')
        return redirect('inicio')

    dependencias = Dependencia.objects.all()
    return render(request, 'prestamo/lista_dependencias.html', {'dependencias': dependencias})

@login_required
def recursos_por_dependencia(request, dependencia_id): 

    dependencia = get_object_or_404(Dependencia, id=dependencia_id)
    recursos_queryset = Recurso.objects.filter(dependencia=dependencia, disponible=True)

    # Agrupar los recursos por tipo
    recursos_agrupados = defaultdict(list)
    for recurso in recursos_queryset:
        recursos_agrupados[recurso.tipo].append(recurso)

    return render(request, 'prestamo/recursos_dependencia.html', {
    'dependencia': dependencia,
    'recursos': dict(recursos_agrupados)
    })

##########################################################################################


## Solicitudes de los prestamos
@login_required
def solicitar_prestamo(request, recurso_id):
    recurso = get_object_or_404(Recurso, id=recurso_id)

    if request.method == 'POST':
        fecha_devolucion = request.POST.get('fecha_devolucion')

        # Crear la solicitud de préstamo
        SolicitudPrestamo.objects.create(
            recurso=recurso,
            usuario=request.user,  # Suponiendo que el usuario autenticado es un estudiante
            fecha_devolucion=fecha_devolucion,
            estado=SolicitudPrestamo.PENDIENTE
        )
    return redirect('recursos_por_dependencia', dependencia_id=recurso.dependencia.id)  # Cambia esto al nombre correcto de tu vista

#Lista para que el administrador pueda ver las solicitudes
@login_required
def lista_solicitudes(request):
    if request.user.rol != 'admin':  # Asegurar que solo los administradores accedan
        return redirect('inicio')

    # Filtrar solicitudes de préstamo solo de la dependencia administrada por el usuario
    solicitudes = SolicitudPrestamo.objects.select_related('recurso', 'usuario').filter(
        recurso__dependencia=request.user.dependencia_administrada
    ).order_by('-fecha_solicitud')

    return render(request, 'admin/solicitudes_prestamo.html', {'solicitudes': solicitudes})


@login_required
def aprobar_solicitud(request, solicitud_id):
    if request.user.rol != "admin":
        return redirect('inicio')

    solicitud = get_object_or_404(SolicitudPrestamo, id=solicitud_id)

    # Verificar que el recurso aún esté disponible
    if not solicitud.recurso.disponible:
        messages.error(request, "El recurso no está disponible.")
        return redirect('lista_solicitudes')

    # Crear el préstamo
    Prestamo.objects.create(
        usuario=solicitud.usuario,
        recurso=solicitud.recurso,
        fecha_devolucion=solicitud.fecha_devolucion
    )

    # Cambiar estado de la solicitud a aprobado
    solicitud.estado = SolicitudPrestamo.APROBADO
    solicitud.save()

    # Marcar el recurso como no disponible
    solicitud.recurso.disponible = False
    solicitud.recurso.save()

    return redirect('lista_solicitudes')


@login_required
def rechazar_solicitud(request, solicitud_id):
    if request.user.rol != "admin":
        return redirect('inicio')

    solicitud = get_object_or_404(SolicitudPrestamo, id=solicitud_id)
    solicitud.estado = SolicitudPrestamo.RECHAZADO
    solicitud.save()
    return redirect('lista_solicitudes')

#Lista para que el estudiante pueda ver sus solicitudes
@login_required
def mis_solicitudes(request):
    if request.user.rol != "estudiante":  # Solo permitir a estudiantes
        return redirect('inicio')

    solicitudes = SolicitudPrestamo.objects.filter(usuario=request.user).select_related('recurso').order_by('-fecha_solicitud')

    return render(request, 'estudiante/mis_solicitudes.html', {'solicitudes': solicitudes})




