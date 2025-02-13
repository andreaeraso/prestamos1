from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Dependencia, Recurso, Prestamo

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'programa', 'rol', 'is_active')
    list_filter = ('rol', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'codigo')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email', 'foto')}),
        ('Información Académica', {'fields': ('codigo', 'programa', 'rol')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'codigo', 'programa', 'rol'),
        }),
    )

@admin.register(Dependencia)
class DependenciaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

@admin.register(Recurso)
class RecursoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'dependencia', 'disponible')
    list_filter = ('disponible', 'dependencia')
    search_fields = ('nombre', 'descripcion')

@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'recurso', 'fecha_prestamo', 'fecha_devolucion', 'devuelto')
    list_filter = ('devuelto', 'fecha_prestamo')
    search_fields = ('usuario__username', 'recurso__nombre')

