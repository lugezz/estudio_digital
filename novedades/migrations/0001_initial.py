# Generated by Django 2.1.7 on 2019-05-31 00:24

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Novedad',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=120)),
                ('contenido', models.TextField()),
                ('activo', models.BooleanField(default=True)),
                ('imagen', models.ImageField(blank=True, null=True, upload_to='image/')),
                ('publicado', models.DateTimeField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('actualizado', models.DateTimeField(auto_now=True)),
                ('asignado_a', models.ManyToManyField(related_name='novedad_users', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-publicado', '-actualizado', '-timestamp'],
            },
        ),
    ]