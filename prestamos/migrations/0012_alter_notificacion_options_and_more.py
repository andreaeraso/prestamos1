# Generated by Django 4.2.7 on 2025-03-14 16:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('prestamos', '0011_notificacion'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='notificacion',
            options={'ordering': ['-fecha_creacion'], 'verbose_name': 'Notificación', 'verbose_name_plural': 'Notificaciones'},
        ),
        migrations.AlterField(
            model_name='notificacion',
            name='usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notificaciones', to=settings.AUTH_USER_MODEL),
        ),
    ]
