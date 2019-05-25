# Generated by Django 2.1.7 on 2019-05-25 12:40

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_auto_20190525_0939'),
    ]

    operations = [
        migrations.AddField(
            model_name='empresa',
            name='mail',
            field=models.CharField(default=django.utils.timezone.now, max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='empresa',
            name='nombre',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]