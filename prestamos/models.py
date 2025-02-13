from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

# Modelo de Dependencia
class Dependencia(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

# Modelo de Usuario (Extiende AbstractUser para roles personalizados)
class Usuario(AbstractUser):
    ADMIN = 'admin'
    ESTUDIANTE = 'estudiante'
    PROFESOR = 'profesor'
    ROLES = [
        (ADMIN, 'Administrador'),
        (ESTUDIANTE, 'Estudiante'),
        (PROFESOR, 'Profesor'),
    ]
    
    # Campos básicos
    rol = models.CharField(max_length=20, choices=ROLES, default=ESTUDIANTE)
    codigo = models.CharField(
        max_length=20, 
        unique=True, 
        null=True,
        blank=True,
        help_text="Código estudiantil o número de identificación"
    )
    programa = models.CharField(
        max_length=100, 
        null=True,
        blank=True,
        help_text="Programa o facultad a la que pertenece"
    )
    foto = models.ImageField(upload_to='usuarios/', null=True, blank=True, help_text="Foto de perfil")
    
    # Nuevo campo para administradores de dependencia
    dependencia_admin = models.ForeignKey(
        Dependencia,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='administradores',
        help_text="Dependencia que administra (solo para administradores)"
    )
    
    # Campos para manejo de permisos
    groups = models.ManyToManyField(Group, related_name="usuarios_personalizados")
    user_permissions = models.ManyToManyField(Permission, related_name="usuarios_personalizados")

    def __str__(self):
        return f"{self.get_rol_display()} - {self.first_name} {self.last_name} ({self.programa})"

    def save(self, *args, **kwargs):
        # Si el usuario no es admin, asegurarse de que no tenga dependencia_admin
        if self.rol != self.ADMIN:
            self.dependencia_admin = None
        super().save(*args, **kwargs)

# Modelo de Recurso
class Recurso(models.Model):
    nombre = models.CharField(max_length=255)
    foto = models.ImageField(upload_to='recursos/', blank=True, null=True)
    color = models.CharField(max_length=50, blank=True)
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
        return f"{self.usuario.username} -> {self.recurso.nombre} ({'Devuelto' if self.devuelto else 'Pendiente'})"
