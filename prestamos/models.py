from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

from django.contrib.auth.models import BaseUserManager

class UsuarioManager(BaseUserManager):
    def create_user(self, codigo, password=None, **extra_fields):
        if not codigo:
            raise ValueError("El usuario debe tener un código único")
        extra_fields.setdefault("is_active", True)
        user = self.model(codigo=codigo, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, codigo, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(codigo=codigo, password=password, **extra_fields)


# Modelo de Dependencia
class Dependencia(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

# Modelo de Usuario (Extiende AbstractUser para roles personalizados)
class Usuario(AbstractUser):
    objects = UsuarioManager()  # Usar el nuevo UserManager

    ADMIN = 'admin'
    ESTUDIANTE = 'estudiante'
    PROFESOR = 'profesor'
    ROLES = [
        (ADMIN, 'Administrador'),
        (ESTUDIANTE, 'Estudiante'),
        (PROFESOR, 'Profesor'),
    ]
    
    username = None  # Elimina el campo username
    rol = models.CharField(max_length=20, choices=ROLES, default=ESTUDIANTE)
    codigo = models.CharField(
        max_length=20, 
        unique=True,  # Asegura que sea único para autenticación
        null=False, 
        blank=False, 
        help_text="Código estudiantil o número de identificación"
    )
    programa = models.CharField(max_length=100, null=True, blank=True, help_text="Programa o facultad a la que pertenece")
    foto = models.ImageField(upload_to='usuarios/', null=True, blank=True, help_text="Foto de perfil")

    dependencia_admin = models.ForeignKey(
        'Dependencia',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='administradores',
        help_text="Dependencia que administra (solo para administradores)"
    )

    groups = models.ManyToManyField(Group, related_name="usuarios_personalizados")
    user_permissions = models.ManyToManyField(Permission, related_name="usuarios_personalizados")

    USERNAME_FIELD = 'codigo'  # Define el campo usado para autenticación
    REQUIRED_FIELDS = []  # No se requiere username ni email

    def __str__(self):
        return f"{self.get_rol_display()} - {self.first_name} {self.last_name} ({self.programa})"

    def save(self, *args, **kwargs):
        if self.rol != self.ADMIN:
            self.dependencia_admin = None
        super().save(*args, **kwargs)

# Modelo de Recurso
class Recurso(models.Model):
    id = models.IntegerField(primary_key=True)
    tipo = models.CharField(max_length=255, default="General")
    nombre = models.CharField(max_length=255)
    foto = models.ImageField(upload_to='recursos/', blank=True, null=True)
    descripcion = models.TextField()
    disponible = models.BooleanField(default=True)
    dependencia = models.ForeignKey(Dependencia, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre} ({'Disponible' if self.disponible else 'No disponible'})"

# Modelo de Préstamo
class Prestamo(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    recurso = models.ForeignKey(Recurso, on_delete=models.CASCADE)
    fecha_prestamo = models.DateTimeField(auto_now_add=True)
    fecha_devolucion = models.DateTimeField()
    firmado = models.ImageField(upload_to='firmas/', blank=True, null=True)
    devuelto = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.usuario.codigo} -> {self.recurso.nombre} ({'Devuelto' if self.devuelto else 'Pendiente'})"

class SolicitudPrestamo(models.Model):
    PENDIENTE = 'pendiente'
    APROBADO = 'aprobado'
    RECHAZADO = 'rechazado'
    
    ESTADOS = [
        (PENDIENTE, 'Pendiente'),
        (APROBADO, 'Aprobado'),
        (RECHAZADO, 'Rechazado'),
    ]

    fecha_solicitud = models.DateTimeField(auto_now_add=True)  # Fecha y hora automática
    recurso = models.ForeignKey(Recurso, on_delete=models.CASCADE)  # Recurso solicitado
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)  # Estudiante que solicita
    fecha_devolucion = models.DateField(help_text="Fecha estimada de devolución")
    estado = models.CharField(max_length=20, choices=ESTADOS, default=PENDIENTE)

    def __str__(self):
        return f"Solicitud de {self.usuario.codigo} para {self.recurso.nombre} - {self.get_estado_display()}"
