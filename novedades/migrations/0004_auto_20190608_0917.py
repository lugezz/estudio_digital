# Generated by Django 2.1.7 on 2019-06-08 12:17

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('novedades', '0003_auto_20190530_2145'),
    ]

    operations = [
        migrations.AlterField(
            model_name='novedad',
            name='publicado',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
