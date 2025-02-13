from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views_api import UsuarioViewSet, DependenciaViewSet, RecursoViewSet, PrestamoViewSet
from .views import (
    login_view, logout_view, registro_view,
    inicio, inventario, crear_prestamo, prestamos_pendientes,
    solicitar_prestamo, agregar_recurso, editar_recurso, eliminar_recurso,
    recursos_no_disponibles, prestamos_lista, nuevo_prestamo, prestamos_activos,
    historial_prestamos, editar_prestamo, marcar_devuelto
)

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)
router.register(r'dependencias', DependenciaViewSet)
router.register(r'recursos', RecursoViewSet)
router.register(r'prestamos', PrestamoViewSet)

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),
    path('', login_view, name='login'),
    path('registro/', registro_view, name='registro'),
    path('logout/', logout_view, name='logout'),
    path('inicio/', inicio, name='inicio'),
    path('inventario/', inventario, name='inventario'),
    path('inventario/agregar/', agregar_recurso, name='agregar_recurso'),
    path('inventario/editar/<int:recurso_id>/', editar_recurso, name='editar_recurso'),
    path('inventario/eliminar/<int:recurso_id>/', eliminar_recurso, name='eliminar_recurso'),
    path('inventario/no-disponibles/', recursos_no_disponibles, name='recursos_no_disponibles'),
    path('prestamos/', prestamos_lista, name='prestamos_lista'),
    path('prestamos/nuevo/', nuevo_prestamo, name='nuevo_prestamo'),
    path('prestamos/activos/', prestamos_activos, name='prestamos_activos'),
    path('prestamos/historial/', historial_prestamos, name='historial_prestamos'),
    path('prestamos/editar/<int:prestamo_id>/', editar_prestamo, name='editar_prestamo'),
    path('prestamos/devolver/<int:prestamo_id>/', marcar_devuelto, name='marcar_devuelto'),
]
