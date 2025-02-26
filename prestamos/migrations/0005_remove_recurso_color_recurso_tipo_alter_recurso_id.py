# Generated by Django 4.2.7 on 2025-02-25 01:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prestamos', '0004_remove_usuario_username_alter_usuario_codigo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recurso',
            name='color',
        ),
        migrations.AddField(
            model_name='recurso',
            name='tipo',
            field=models.CharField(default='General', max_length=255),
        ),
        migrations.AlterField(
            model_name='recurso',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
