# Usamos la imagen oficial de Python
FROM python:3.11

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos el contenido del proyecto al contenedor
COPY . /app

# Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponemos el puerto en el que correrá Django
EXPOSE 8000

# Comando para iniciar el servidor
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
