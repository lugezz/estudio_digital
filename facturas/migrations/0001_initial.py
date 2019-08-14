# Generated by Django 2.2.3 on 2019-08-10 13:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='IVA',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_iva', models.CharField(choices=[('compras', 'Compras'), ('ventas', 'Ventas')], default='ventas', max_length=20)),
                ('periodo', models.DateField()),
                ('neto_gravado', models.DecimalField(decimal_places=2, max_digits=10)),
                ('neto_no_gravado', models.DecimalField(decimal_places=2, max_digits=10)),
                ('exento', models.DecimalField(decimal_places=2, max_digits=10)),
                ('iva', models.DecimalField(decimal_places=2, max_digits=10)),
                ('percepcion', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='Creado el')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='factura_created_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
