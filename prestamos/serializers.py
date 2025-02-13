from rest_framework import serializers
from .models import Usuario, Dependencia, Recurso, Prestamo  # Importamos Usuario directamente

# Serializador de Usuario
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario  # Aseguramos que se usa el modelo correcto
        fields = ['id', 'username', 'email', 'rol', 'dependencia']

# Serializador de Dependencias
class DependenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dependencia
        fields = '__all__'

# Serializador de Recursos
class RecursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recurso
        fields = '__all__'

# Serializador de Préstamos
class PrestamoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prestamo
        fields = '__all__'
